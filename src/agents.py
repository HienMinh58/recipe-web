from pymilvus import Collection, connections, utility, MilvusClient
from sentence_transformers import SentenceTransformer
import nltk 
import logging
nltk.download('stopwords')
nltk.download('punkt_tab')
from nltk.corpus import stopwords

stop_words_en = list(stopwords.words('english'))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
import os
ZILLIZ_CLOUD_ENDPOINT = os.getenv("ZILLIZ_CLOUD_ENDPOINT")
ZILLIZ_CLOUD_API_KEY = os.getenv("ZILLIZ_CLOUD_API_KEY") 
COLLECTION_NAME = "recipes"
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, create_react_agent
from langchain.prompts import PromptTemplate
import os

try:
    connections.connect("default", uri=ZILLIZ_CLOUD_ENDPOINT, token=ZILLIZ_CLOUD_API_KEY, secure=True)
    logger.info("Connect to Milvus at port 19530")
    logger.info("Current collections: %s", utility.list_collections())
except Exception as e:
    logger.error(f"Error connect: {e}")
    raise

class Agent:
    def __init__(self, role: str, model: str="openai/gpt-4o-mini", tools: list = None):
        """_summary_

        Args:
            role (str): The role of the agent (e.g., 'Router', 'Retrieval').
            model (str, optional): The language model to be used by the agent. Defaults to "openai/gpt-4o-mini".
            tools (list, optional): A list of tools the agent can use (e.g., RAG query tool). Defaults to None.
        """
        self.role = role
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPEN_ROUTER_API"),
            base_url="https://openrouter.ai/api/v1",
            model=model
        )
        self.tools = tools or []
        self.agent = self._build_agent()
        
    def _build_agent(self):
        prompt_template = """
    You are {role}, an agent designed to process queries using available tools.

    Tools available: {tool_names}

    You can use the following tools:
    {tools}

    To answer the query, follow these steps:
    1. Analyze the query to determine which tool(s) to use, if any.
    2. Use the selected tool(s) to gather necessary information.
    3. Provide a clear and concise final answer.

    Query: {query}

    Agent's scratchpad (for intermediate thoughts and tool results):
    {agent_scratchpad}

    Format your response as follows:
    - If using a tool, show your reasoning and tool usage.
    - End with: [FINAL ANSWER] Your final answer here
    """
        prompt = PromptTemplate.from_template(prompt_template)
        return create_react_agent(llm=self.llm, tools=self.tools, prompt=prompt)
    
    def run(self, query: str):
        """Run agent with query. """
        return self.agent.invoke({"query": query, "intermediate_steps": [], "role": self.role})
    
class RetrievalAgent(Agent):
    def __init__(self):
        
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')  
        milvus_tool = Tool(
            name="milvus_retriver",
            func=self._rag,
            description="Find recipes from Milvus with top_k and metric type."
        )
        
        super().__init__(role="RetrievalAgent", tools=[milvus_tool])
    
    def _rag(self, query: str, top_k: int = 5, metric_type: str = "COSINE") -> list[dict]:
        if not utility.has_collection("recipes"):
            raise ValueError("Collection 'recipes' does not exist!")
        col = Collection(COLLECTION_NAME)
        
        try:
            col.load()
        except Exception as e:
            logger.error(f"Error loading collection: {e}")
            raise
        
        rm_st_qr = ' '.join(word for word in nltk.word_tokenize(query.lower()) if word not in stop_words_en)
        
        query_vector = self.embed_model.encode([rm_st_qr])[0].tolist()
        logger.debug(f"Query after preprocessing: {rm_st_qr}")

        search_params = {
            "metric_type": metric_type,
            "params": {"nprobe": 16}
        }
        
        results = col.search(
            data=[query_vector],
            anns_field="text_dense_vector",
            param=search_params,
            limit=top_k,
            output_fields=["recipe_id", "name", "timestamp", "text"]
        )
        output = []
        for hits in results:
            for hit in hits:
                entity = hit.entity
                output.append({
                    "recipe_id": entity.get("recipe_id"),
                    "name": entity.get("name"),
                    "timestamp": entity.get("timestamp"),
                    "text": entity.get("text"),
                    "distance": hit.distance
                })
        return output

class RouterAgent(Agent):
    def __init__(self):
        classify_tools = Tool(
            name="classify_query",
            func=self._classify_query,
            description="Classify query into 'relevant_recipe', 'off_topic', or 'recommendation'."
        )
        super().__init__(role="Router Agent", tools=[classify_tools])

    def _classify_query(self, query: str) -> str:
        prompt = PromptTemplate.from_template(
        """You are a Router Agent. Classify the following query into one of these types: 
        - 'relevant_recipe' (related to cooking recipes), 
        - 'off_topic' (unrelated), 
        - 'recommendation' (request for personalized recommendations). 
        Query: {query} 
        Return only one word: 'relevant_recipe', 'off_topic', or 'recommendation'."""
        )
        
        response = self.llm.invoke(prompt.format(query=query))
        return response.content.strip()
    
    def run(self, query: str) -> tuple[str, str]:
        """Run agent and return query type and query has processed"""
        classification = self._classify_query(query)
        return classification, query
    
class GenerationAgent(Agent):
    def __init__(self):
        super().__init__(role="Generation Agent")
    
    def run(self, query: str, retrieved_data: list = None) -> str:
        if retrieved_data is None:
            retrieved_data = []
        
        prompt = PromptTemplate.from_template(
            """You are a Generation Agent. Based on the query and retrieved data, generate a friendly response: 
            - Query: {query} 
            - Retrieved Data: {retrieved_data} 
            Return the response as clear text, for example: a list of recipes or cooking instructions."""
        )
        
        response = self.llm.invoke(prompt.format(query=query, retrieved_data=retrieved_data))
        return response.content.strip()
    
# router_agent = RouterAgent()
# retrieval_agent = RetrievalAgent()
# generation_agent = GenerationAgent()

# query = "Recipes that make from chickens"
# classification, processed_query = router_agent.run(query=query)
# print(f"Classification: {classification}")

# if classification == "relevant_recipe":
#     retrieved_results = retrieval_agent.run(processed_query)
#     response = generation_agent.run(retrieved_data=retrieved_results)
#     print(f"Generated Response: {response}")
# else:
#     print(f"Query is not related to recipe. Please ask about recipes!")
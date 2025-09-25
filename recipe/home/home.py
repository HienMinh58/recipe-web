import random
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from recipe.adapters.memory_repo import MemoryRepository
from src.agents import RouterAgent, RetrievalAgent, GenerationAgent  # Import your agent classes
import logging

logger = logging.getLogger(__name__)

home_bp = Blueprint('home', __name__)
repo = MemoryRepository()

# Initialize agents
router_agent = RouterAgent()
retrieval_agent = RetrievalAgent()
generation_agent = GenerationAgent()

@home_bp.route('/')
def home():
    all_recipes = repo.get_all_recipes()
    featured_recipes = random.sample(all_recipes, k=4)
    
    # Check if chatbot dialog should be shown
    show_chatbot = request.args.get('show_chatbot', '0') == '1'
    logger.info(f"show_chatbot: {show_chatbot}")    # Get conversation history from session
    conversation = session.get('conversation', [])
    
    return render_template(
        'home.html',
        recipes=featured_recipes,
        show_chatbot=show_chatbot,
        conversation=conversation
    )

@home_bp.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    query = request.args.get('msg', '').strip()
    if not query:
        return jsonify({"reply": "Hi! How can I help you today?"})

    try:
        # Step 1: Router decides query type
        query_type, processed_query = router_agent.run(query)
        logger.info(f"Router classified query='{query}' as {query_type}")

        reply = ""
        retrieved_data = []

        # Step 2: If relevant → use retrieval first
        if query_type == "relevant_recipe":
            retrieved_data = retrieval_agent._rag(processed_query)
            reply = generation_agent.run(processed_query, retrieved_data)
        else:
            # For off_topic or recommendation → generate directly
            reply = generation_agent.run(processed_query)

        # Step 3: Save conversation in session
        conversation = session.get("conversation", [])
        conversation.append({"user": query, "bot": reply})
        session["conversation"] = conversation

        return jsonify({"reply": reply})

    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        return jsonify({"reply": "Sorry! Please try again later."})
    
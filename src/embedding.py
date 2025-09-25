from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import logging
from sentence_transformers import SentenceTransformer
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from recipe.adapters.memory_repo import MemoryRepository

repo = MemoryRepository()
model = SentenceTransformer('all-MiniLM-L6-v2')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

collection = None

def text_prepare() -> list:
    recipes = repo.get_all_recipes()
    texts = []
    quantities = [recipe.ingredient_quantities for recipe in recipes if recipe is not None]
    ingredients = [recipe.ingredients for recipe in recipes if recipe is not None]
    instructions = [recipe.instructions for recipe in recipes if recipe is not None]
    ingrs = []
    for qt, ig in zip(quantities, ingredients):
        ingr = list(zip(qt, ig))
        ingrs.append(ingr)
    
    formated_igrs = []
    formated_instrs = []
    for instr in instructions:
        formated_instr = ', '.join(instr)
        formated_instrs.append(formated_instr)
    for ingr in ingrs:
        formated_igr = ', '.join(f"{qty} {igr}" for qty, igr in ingr)
        formated_igrs.append(formated_igr)

    for i, recipe in enumerate(recipes):
        text = f"Recipe: {recipes[i].id}, Description: {recipes[i].description}, Ingredients: {formated_igrs[i]}, Instructions: {formated_instrs[i]}"
        texts.append(text)
    
    return texts

def init_milvus_collection(drop_existing: bool = False):
    try:
        if not connections.has_connection("default"):
            connections.connect("default", host="localhost", port="19530")
            logger.debug("Connected to Milvus at localhost:19530")
    except Exception as e:
        logger.error(f"Failed to connect to Milvus: {e}")
        raise
    
    if drop_existing and utility.has_collection("recipes"):
        utility.drop_collection("recipes")
        logger.debug("Dropped existing collection 'recipes'")

    meta_fields = [
        FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=255),
        FieldSchema(name="timestamp", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=10000, enable_analyzer=True),
    ]
    
    if not utility.has_collection('recipes'):
        fields = [
            FieldSchema(name="recipe_id", dtype=DataType.INT64, is_primary=True, auto_id=False),  # Sửa auto_id=False
            FieldSchema(name="text_dense_vector", dtype=DataType.FLOAT_VECTOR, dim=384),
            *meta_fields
        ]
        
        schema = CollectionSchema(fields=fields, description="text embedding with metadata")
        col = Collection(name="recipes", schema=schema)  # Sửa tên thành "recipes"
        logger.debug("Created new collection 'recipes'")
    else:
        col = Collection(name='recipes')
        logger.debug("Loaded existing collection 'recipes'")
        
    if not col.has_index():
        try:
            index_params = {"metric_type": "COSINE", "index_type": "IVF_FLAT", "params": {"nlist": 128}}
            col.create_index(field_name="text_dense_vector", index_params=index_params)
            logger.debug("Created index for 'text_dense_vector' field")
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            raise
    try:
        col.load()
        logger.debug("Collection loaded")
    except Exception as e:
        logger.error(f"Failed to load collection: {e}")
        raise

    return col

def init_collection():
    global collection
    if collection is None:
        collection = init_milvus_collection(drop_existing=True)

def embed_text(text: str) -> list:
    embedding = model.encode(text).tolist()
    logger.debug(f"Generated embedding for text (length: {len(embedding)})")
    return embedding

def insert_embeding(recipes: list):
    global collection
    if collection is None:
        raise ValueError("Uninitialize collection")
    
    df = pd.read_csv("recipe/adapters/data/recipes.csv")
    texts = text_prepare()
    if df.empty or not texts:
        raise ValueError("No data or texts to insert")
    
    df['text'] = texts
    entities = [[], [], [], [], []]  # recipe_id, text_dense_vector, name, timestamp, text
    
    for _, row in df.iterrows():
        embedding = embed_text(row["text"])
        entities[0].append(row["RecipeId"])          # recipe_id
        entities[1].append(embedding)                # text_dense_vector
        entities[2].append(row["Name"])              # name
        entities[3].append(row["DatePublished"])     # timestamp
        entities[4].append(row["text"])              # text
    
    try:
        mr = collection.insert(entities)
        logger.debug(f"Inserted {mr.insert_count} entities")

        collection.flush()
        logger.debug("Flushed data to Milvus")
        
        collection.release()
        collection.load()
        logger.debug("Collection reloaded after flush")
    except Exception as e:
        logger.error(f"Failed to insert entities: {e}")
        raise

try:
    texts = text_prepare()
    recipes = repo.get_all_recipes()
    init_collection()
    insert_embeding(recipes=recipes)
    search_params = {"metric_type": "COSINE", "params": {"nprobe": 16}}
    query_vector = model.encode("A frozen dessert recipe").tolist()

    results = collection.search(
        data=[query_vector],
        anns_field="text_dense_vector",
        param=search_params,
        limit=5,
        output_fields=["recipe_id", "name"]  # Sửa tên field
    )

    for result in results[0]:
        print(f"ID: {result.id}, Distance: {result.distance}, Name: {result.entity.get('name')}")
except Exception as e:
    logger.error(f"Error in main execution: {e}")
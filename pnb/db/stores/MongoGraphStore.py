from langchain_mongodb.graphrag.graph import MongoDBGraphStore
from pnb.langgraph.utils import OPENAI_LLM
from pnb import SETTINGS

MONGO_GRAPH_STORE = MongoDBGraphStore(
    connection_string=SETTINGS.MONGO_URI,
    database_name=SETTINGS.DB_NAME,
    collection_name="knowledge_graph",
    entity_extraction_model=OPENAI_LLM,
)

from langchain_core.tools import tool
from pnb.db.stores.MongoGraphStore import MONGO_GRAPH_STORE


@tool
def retriever_tool(query: str):
    """
    RAG Retrieval Tool

    Args:
        query

    Returns:
        str
    """
    return MONGO_GRAPH_STORE.chat_response(query=query)

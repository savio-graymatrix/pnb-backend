import os
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from langchain_mongodb import MongoDBGraphStore
from langchain_openai import ChatOpenAI  # Or any LLM you prefer
from langchain_core.exceptions import LangChainException
from pymongo import MongoClient
from pnb import SETTINGS

# Environment variables or settings for MongoDB connection
# Assume these are set in your environment or a settings module
MONGODB_CONNECTION_STRING = SETTINGS.MONGO_URI
MONGODB_DATABASE_NAME = SETTINGS.MONGO_DB
DEFAULT_LLM_MODEL = ChatOpenAI(
    model="gpt-4o-mini", temperature=0
)  # Default LLM for entity extraction and querying

# Cache graph stores for different collections to avoid reinitializing
_graph_stores: Dict[str, MongoDBGraphStore] = {}


def get_or_create_graph_store(
    database_name: str,
    collection_name: str,
    entity_extraction_model: Optional[Any] = None,
) -> MongoDBGraphStore:
    """
    Get or create a MongoDBGraphStore instance for the specified database and collection.
    """
    key = f"{database_name}.{collection_name}"
    if key not in _graph_stores:
        try:
            graph_store = MongoDBGraphStore(
                connection_string=MONGODB_CONNECTION_STRING,
                database_name=database_name,
                collection_name=collection_name,
                entity_extraction_model=entity_extraction_model or DEFAULT_LLM_MODEL,
                # Additional optional parameters: e.g., node_label_field='type', relationship_label_field='relation'
            )
            _graph_stores[key] = graph_store
        except Exception as e:
            raise LangChainException(
                f"Failed to initialize MongoDBGraphStore for {key}: {str(e)}"
            )
    return _graph_stores[key]


@tool
async def graph_rag_query(
    query: str,
    database_name: str = MONGODB_DATABASE_NAME,
    collection_name: str = "default_graph_collection",
    add_documents: Optional[list] = None,
    llm_model_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Perform a GraphRAG query on a MongoDB collection to traverse entities and relationships.

    This tool uses MongoDBGraphStore to query a knowledge graph stored in MongoDB.
    It can optionally add new documents to the graph before querying.

    Args:
        query (str): The natural language query to ask the graph (e.g., "What is the connection between Company A and Company B?").
        database_name (str, optional): The MongoDB database name containing the graph collection. Defaults to environment setting.
        collection_name (str, optional): The MongoDB collection name storing the graph (entities and relationships). Defaults to 'default_graph_collection'.
        add_documents (list, optional): A list of documents (as strings or dicts) to add to the graph before querying. Useful for updating the graph dynamically.
        llm_model_name (str, optional): The LLM model name to use for entity extraction (e.g., 'gpt-4o'). Defaults to 'gpt-4o-mini'.

    Returns:
        Dict[str, Any]: A dictionary with 'success' (bool), 'answer' (str), and optional 'error' (str).
    """
    try:
        # Initialize LLM for entity extraction if specified
        entity_extraction_model = None
        if llm_model_name:
            entity_extraction_model = ChatOpenAI(model=llm_model_name, temperature=0)

        # Get or create the graph store
        graph_store = get_or_create_graph_store(
            database_name, collection_name, entity_extraction_model
        )

        # Optionally add documents to the graph
        if add_documents:
            # Assume add_documents is a list of strings or Document objects
            graph_store.add_documents(add_documents)
            # Refresh or reindex if necessary (MongoDBGraphStore handles this internally)

        # Perform the chat response query
        response = graph_store.chat_response(query)
        return {
            "success": True,
            "answer": response.content,
            "metadata": {
                "database": database_name,
                "collection": collection_name,
                "query": query,
            },
        }
    except Exception as e:
        return {"success": False, "error": f"GraphRAG query failed: {str(e)}"}


# Example usage (for testing outside LangChain agent)
# if __name__ == "__main__":
#     import asyncio

#     async def test_graph_rag():
#         # Example: Add some sample documents (if the graph is empty)
#         sample_docs = [
#             "Company A is managed by Person X. Person X reports to Person Y at Company B.",
#             "Company B invests in Company A."
#         ]
#         result = await graph_rag_query(
#             query="What is the connection between Company A and Company B?",
#             add_documents=sample_docs,
#             collection_name="test_graph"
#         )
#         print(result)

#     asyncio.run(test_graph_rag())

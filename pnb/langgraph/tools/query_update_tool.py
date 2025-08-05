from langchain_core.tools import tool
from pnb.db.data_models.procurement.Query import Query


@tool
async def query_update_tool(response: str, query_id: str):
    """
    Updates the query in the database.

    Args:
    response: str
    query_id: str

    Returns:
    "Query updated successfully" if the query was updated else "Query not found"
    """
    query = await Query.get(query_id)
    if not query:
        raise ValueError("Query not found")
    query.response = response
    await query.save()
    return "Query updated successfully"

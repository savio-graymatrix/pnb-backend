from langchain_tavily import TavilySearch
from langchain_core.tools import tool


@tool
async def web_search_tool(query: str):
    """Tool to search the web for relevant information"""
    tool = TavilySearch(max_results=2)
    return tool.invoke(query)
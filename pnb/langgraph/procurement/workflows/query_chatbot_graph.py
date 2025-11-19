from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from pnb.langgraph.procurement.agents.query_chatbot_agent import QueryChatbotAgent
from langgraph.checkpoint.memory import MemorySaver
# from bpcl.agentic.workflows import *

async def setup_query_chatbot_graph(checkpointer: Checkpointer = MemorySaver()) -> None:
    query_chatbot_graph_builder = StateGraph(MessagesState)
    query_chatbot_graph_builder.add_node("query_chatbot_agent", QueryChatbotAgent.chatbot, metadata={"node_type":"query_chatbot_agent"})
    query_chatbot_graph_builder.add_edge(START, "query_chatbot_agent")
    query_chatbot_graph_builder.add_edge("query_chatbot_agent", END)
    return query_chatbot_graph_builder.compile(
        checkpointer=checkpointer,
    )
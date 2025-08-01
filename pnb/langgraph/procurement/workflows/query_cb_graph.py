from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from pnb.langgraph.procurement.agents.query_chatbot_agent import QueryChatbotAgent
from langgraph.checkpoint.memory import MemorySaver
# from bpcl.agentic.workflows import *

async def setup_query_cb_graph(checkpointer: Checkpointer = MemorySaver()) -> None:
    instruction_graph_builder = StateGraph(MessagesState)
    instruction_graph_builder.add_node("query_cb_agent", QueryChatbotAgent.chatbot, metadata={"node_type":"query_cb_agent"})
    instruction_graph_builder.add_edge(START, "query_cb_agent")
    instruction_graph_builder.add_edge("query_cb_agent", END)
    return instruction_graph_builder.compile(
        checkpointer=checkpointer,
    )
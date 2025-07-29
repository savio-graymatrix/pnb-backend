from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from pnb.langgraph.procurement.agents.mini_chatbot_agent import MiniChatbotAgent
from langgraph.checkpoint.memory import MemorySaver
# from bpcl.agentic.workflows import *

async def setup_mini_cb_graph(checkpointer: Checkpointer = MemorySaver()) -> None:
    instruction_graph_builder = StateGraph(MessagesState)
    instruction_graph_builder.add_node("mini_cb_agent", MiniChatbotAgent.chatbot, metadata={"node_type":"mini_cb_agent"})
    instruction_graph_builder.add_edge(START, "mini_cb_agent")
    instruction_graph_builder.add_edge("mini_cb_agent", END)
    return instruction_graph_builder.compile(
        checkpointer=checkpointer,
    )
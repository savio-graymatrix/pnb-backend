from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from pnb.langgraph.procurement.agents.review_chatbot_agent import ReviewChatbotAgent
from langgraph.checkpoint.memory import MemorySaver

async def setup_review_cb_graph(checkpointer: Checkpointer = MemorySaver()) -> None:

    global reviewgraph

    rcbgraph_builder = StateGraph(MessagesState)
    rcbgraph_builder.add_node(
        "reviewer", ReviewChatbotAgent.chatbot, metadata={"node_type": "reviewer"}
    )
    rcbgraph_builder.add_edge(START, "reviewer")
    rcbgraph_builder.add_edge("reviewer", END)
    return rcbgraph_builder.compile(
        checkpointer=checkpointer,
    )
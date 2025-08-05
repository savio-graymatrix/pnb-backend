from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from pnb.langgraph.procurement.agents.review_chatbot_agent import ReviewChatbotAgent
from langgraph.checkpoint.memory import MemorySaver

async def setup_review_chatbot_graph(checkpointer: Checkpointer = MemorySaver()) -> None:

    global reviewgraph

    rcbgraph_builder = StateGraph(MessagesState)
    rcbgraph_builder.add_node(
        "review_chatbot_agent", ReviewChatbotAgent.chatbot, metadata={"node_type": "review_chatbot_agent"}
    )
    rcbgraph_builder.add_edge(START, "review_chatbot_agent")
    rcbgraph_builder.add_edge("review_chatbot_agent", END)
    return rcbgraph_builder.compile(
        checkpointer=checkpointer,
    )
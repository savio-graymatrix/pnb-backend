from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.checkpoint.memory import MemorySaver
from pnb.langgraph.sales.agents.sales_chatbot import SalesChatbotagent

async def setup_sales_chatbot_graph(checkpointer: Checkpointer = MemorySaver()) -> None:
    sales_graph_builder = StateGraph(MessagesState)
    sales_graph_builder.add_node(
        "sales_chatbot", SalesChatbotagent.sales_chatbot, metadata={"node_type":"sales_chatbot"}
    )
    sales_graph_builder.add_edge(START, "sales_chatbot")
    sales_graph_builder.add_edge("sales_chatbot", END)
    return sales_graph_builder.compile(checkpointer=checkpointer)
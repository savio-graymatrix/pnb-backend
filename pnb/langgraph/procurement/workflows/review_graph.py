from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from pnb.langgraph.procurement.agents.review_agent import ReviewAgent
from langgraph.checkpoint.memory import MemorySaver

async def setup_review_graph(checkpointer: Checkpointer = MemorySaver()) -> None:

    global reviewgraph

    rgraph_builder = StateGraph(MessagesState)
    rgraph_builder.add_node(
        "reviewer", ReviewAgent.review, metadata={"node_type": "reviewer"}
    )
    rgraph_builder.add_edge(START, "reviewer")
    rgraph_builder.add_edge("reviewer", END)
    return rgraph_builder.compile(
        checkpointer=checkpointer,
    )
 
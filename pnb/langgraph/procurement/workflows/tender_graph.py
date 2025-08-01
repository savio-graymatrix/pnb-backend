from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.checkpoint.memory import MemorySaver
from pnb.langgraph.procurement.agents.tender_agent import TenderAgent



async def setup_tender_graph(checkpointer: Checkpointer = MemorySaver()) -> None:

    global tendergraph

    tendergraph_builder = StateGraph(MessagesState)
    tendergraph_builder.add_node(
        "tender", TenderAgent.tender, metadata={"node_type": "tender"}
    )
    tendergraph_builder.add_edge(START, "tender")
    tendergraph_builder.add_edge("tender", END)
    return tendergraph_builder.compile(
        checkpointer=checkpointer,
    )
 
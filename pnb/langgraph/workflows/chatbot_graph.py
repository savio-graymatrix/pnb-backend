from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from pnb.langgraph.agents.supervisor import SupervisorAgent
from pnb.langgraph.agents.PAN import PANAgent
from pnb.langgraph.agents.AADHAR import AADHARAgent
from pnb.langgraph.agents.credit import CreditAgent
from langgraph.checkpoint.memory import MemorySaver



async def setup_credit_graph(checkpointer: Checkpointer = MemorySaver()) -> None:

    global creditgraph

    cgraph_builder = StateGraph(MessagesState)
    cgraph_builder.add_node(
        "credit", CreditAgent.credit_agent, metadata={"node_type": "credit"}
    )
    cgraph_builder.add_edge(START, "credit")
    cgraph_builder.add_edge("credit", END)
    return cgraph_builder.compile(
        checkpointer=checkpointer,
    )
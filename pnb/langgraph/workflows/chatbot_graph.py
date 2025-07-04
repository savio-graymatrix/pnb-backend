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
        "chatbot", ChatbotAgent.chatbot, metadata={"node_type": "chatbot"}
    )
    cgraph_builder.add_edge(START, "chatbot")
    cgraph_builder.add_edge("chatbot", END)
    return cgraph_builder.compile(
        checkpointer=checkpointer,
    )
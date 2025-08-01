from langgraph.graph import StateGraph
from langgraph.types import Checkpointer
from pnb.langgraph.procurement.agents.tender_cb_agent import TenderChatbotAgent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, MessagesState, END

async def setup_tender_cb_graph(checkpointer:Checkpointer = MemorySaver()):
    tendercbgraph_builder = StateGraph(MessagesState)
    tendercbgraph_builder.add_node("tender_cb_agent", TenderChatbotAgent.chatbot, metadata={"node_type":"tender_cb_agent"})
    tendercbgraph_builder.add_edge(START, "tender_cb_agent")
    tendercbgraph_builder.add_edge("tender_cb_agent", END)
    return tendercbgraph_builder.compile(
        checkpointer=checkpointer,
    )
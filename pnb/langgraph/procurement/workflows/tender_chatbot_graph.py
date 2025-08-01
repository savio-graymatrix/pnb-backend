from langgraph.graph import StateGraph
from langgraph.types import Checkpointer
from pnb.langgraph.procurement.agents.tender_chatbot_agent import TenderChatbotAgent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, MessagesState, END

async def setup_tender_chatbot_graph(checkpointer:Checkpointer = MemorySaver()):
    tendercbgraph_builder = StateGraph(MessagesState)
    tendercbgraph_builder.add_node("tender_chatbot_agent", TenderChatbotAgent.chatbot, metadata={"node_type":"tender_chatbot_agent"})
    tendercbgraph_builder.add_edge(START, "tender_chatbot_agent")
    tendercbgraph_builder.add_edge("tender_chatbot_agent", END)
    return tendercbgraph_builder.compile(
        checkpointer=checkpointer,
    )
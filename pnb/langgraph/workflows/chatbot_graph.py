from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
# from pnb.langgraph.agents.supervisor import SupervisorAgent
# from pnb.langgraph.agents.PAN import PANAgent
# from pnb.langgraph.agents.AADHAR import AADHARAgent
# from pnb.langgraph.agents.credit import CreditAgent
from langgraph.checkpoint.memory import MemorySaver
from pnb.langgraph.agents.chatbot_agent import ChatbotAgent



async def setup_chatbot_graph(checkpointer: Checkpointer = MemorySaver()) -> None:

    global chatbotgraph

    cgraph_builder = StateGraph(MessagesState)
    cgraph_builder.add_node(
        "chatbot", ChatbotAgent.chatbot, metadata={"node_type": "chatbot"}
    )
    cgraph_builder.add_edge(START, "chatbot")
    cgraph_builder.add_edge("chatbot", END)
    return cgraph_builder.compile(
        checkpointer=checkpointer,
    )
from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from pnb.langgraph.procurement.agents.tender_rule_agent import TenderRuleAgent
from langgraph.checkpoint.memory import MemorySaver
# from bpcl.agentic.workflows import *

async def setup_tender_rule_graph(checkpointer: Checkpointer = MemorySaver()) -> None:
    tender_rule_graph_builder = StateGraph(MessagesState)
    tender_rule_graph_builder.add_node("tender_rule_agent", TenderRuleAgent.tender_rule_agent, metadata={"node_type":"tender_rule_agent"})
    tender_rule_graph_builder.add_edge(START, "tender_rule_agent")
    tender_rule_graph_builder.add_edge("tender_rule_agent", END)
    return tender_rule_graph_builder.compile(
        checkpointer=checkpointer,
    )
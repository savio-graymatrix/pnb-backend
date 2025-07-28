from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from pnb.langgraph.procurement.agents.instruction_agent import InstructionAgent
from langgraph.checkpoint.memory import MemorySaver
# from bpcl.agentic.workflows import *

async def setup_instruction_graph(checkpointer: Checkpointer = MemorySaver()) -> None:
    instruction_graph_builder = StateGraph(MessagesState)
    instruction_graph_builder.add_node("instruction_agent", InstructionAgent.instruction_agent, metadata={"node_type":"instruction_agent"})
    instruction_graph_builder.add_edge(START, "instruction_agent")
    instruction_graph_builder.add_edge("instruction_agent", END)
    return instruction_graph_builder.compile(
        checkpointer=checkpointer,
    )
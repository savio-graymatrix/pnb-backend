from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from pnb.langgraph.agents.instruction_agent import InstructionAgent
from langgraph.checkpoint.memory import MemorySaver

async def setup_project_graph(checkpointer: Checkpointer = MemorySaver()) -> None:
    project_graph_builder = StateGraph(MessagesState)
    project_graph_builder.add_node("instruction_agent", InstructionAgent.instruction_agent, metadata={"node_type":"instruction_agent"})
    project_graph_builder.add_edge(START, "instruction_agent")
    project_graph_builder.add_edge("instruction_agent", END)
    return project_graph_builder.compile(
        checkpointer=checkpointer,
    )
from botocore.compat import set_socket_timeout
from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.checkpoint.memory import MemorySaver
from pnb.langgraph.procurement.agents.query_agent import QueryAgent

async def setup_query_graph(checkpointer:Checkpointer=MemorySaver())-> None:
    global querygraph

    qgraph_builder = StateGraph(MessagesState)
    qgraph_builder.add_node("query_agent", QueryAgent.query_agent, metadata={"node_type":"query_agent"})
    qgraph_builder.add_edge(START, "query_agent")
    qgraph_builder.add_edge("query_agent", END)
    return qgraph_builder.compile(checkpointer=checkpointer)
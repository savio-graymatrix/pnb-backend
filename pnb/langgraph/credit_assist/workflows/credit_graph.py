from langgraph.types import Checkpointer
from langgraph.checkpoint.memory import MemorySaver
from pnb.langgraph.credit_assist.agents.supervisor import credit_supervisor

async def setup_credit_graph(checkpointer: Checkpointer = MemorySaver()):
    supervisor = await credit_supervisor()
    app = supervisor.compile()
    return app
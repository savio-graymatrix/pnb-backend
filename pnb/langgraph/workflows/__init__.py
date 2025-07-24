from pnb import LOGGER, SETTINGS
import os
from pnb.langgraph.workflows.project_graph import setup_project_graph
from pnb.langgraph.workflows.credit_graph import setup_credit_graph
from pnb.langgraph.workflows.chatbot_graph import setup_chatbot_graph
from pnb.db.stores.MongoStore import MONGO_STORE
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver

GRAPHS = dict()


async def setup_graphs():
    checkpointer = AsyncMongoDBSaver(MONGO_STORE.client,db_name=SETTINGS.DB_NAME)
    GRAPHS.update(
        {
            "project": await setup_project_graph(checkpointer=checkpointer),
            "credit": await setup_credit_graph(checkpointer=checkpointer),
            "chatbot": await setup_chatbot_graph(checkpointer=checkpointer),
        }
    )
    for key, graph in GRAPHS.items():
        os.makedirs(f"{os.getcwd()}/docs", exist_ok=True)
        os.makedirs(f"{os.getcwd()}/docs/images", exist_ok=True)
        graph.get_graph().draw_mermaid_png(output_file_path=f"docs/images/{key}.png")
    LOGGER.info(
        f"Graphs initialized:\n{"\n".join([f"{key}:{graph}" for key,graph in GRAPHS.items()])}"
    )

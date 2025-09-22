from langgraph.checkpoint.base import Checkpoint
from pnb import LOGGER, SETTINGS
import os
from pnb.langgraph.sales.workflows.sales_chatbot_graph import setup_sales_chatbot_graph
from pnb.db.stores.MongoStore import MONGO_STORE
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver

SALES_GRAPHS = dict()


async def compile_sales_graphs():
    checkpointer = AsyncMongoDBSaver(MONGO_STORE.client, db_name=SETTINGS.DB_NAME)
    SALES_GRAPHS.update(
        {
            "sales_chatbot": await setup_sales_chatbot_graph(checkpointer=checkpointer),
        }
    )
    for key, graph in SALES_GRAPHS.items():
        os.makedirs(f"{os.getcwd()}/docs", exist_ok=True)
        os.makedirs(f"{os.getcwd()}/docs/images", exist_ok=True)
        # graph.get_graph().draw_mermaid_png(output_file_path=f"docs/images/{key}.png")
    LOGGER.info(
        f"Sales Graphs initialized:\n{"\n".join([f"{key}:{graph}" for key,graph in SALES_GRAPHS.items()])}"
    )

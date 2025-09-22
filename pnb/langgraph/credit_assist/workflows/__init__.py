from pnb import LOGGER, SETTINGS
import os
from pnb.langgraph.credit_assist.workflows.project_graph import setup_project_graph
from pnb.langgraph.credit_assist.workflows.credit_graph import setup_credit_graph
from pnb.langgraph.credit_assist.workflows.chatbot_graph import setup_chatbot_graph
from pnb.db.stores.MongoStore import MONGO_STORE
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver

CREDIT_ASSIST_GRAPHS = dict()


async def compile_credit_assist_graphs():
    checkpointer = AsyncMongoDBSaver(MONGO_STORE.client,db_name=SETTINGS.DB_NAME)
    CREDIT_ASSIST_GRAPHS.update(
        {
            "project": await setup_project_graph(checkpointer=checkpointer),
            "credit": await setup_credit_graph(checkpointer=checkpointer),
            "chatbot": await setup_chatbot_graph(checkpointer=checkpointer),
        }
    )
    for key, graph in CREDIT_ASSIST_GRAPHS.items():
        os.makedirs(f"{os.getcwd()}/docs", exist_ok=True)
        os.makedirs(f"{os.getcwd()}/docs/images", exist_ok=True)
        # graph.get_graph().draw_mermaid_png(output_file_path=f"docs/images/{key}.png")
    LOGGER.info(
        f"Credit Assist Graphs initialized:\n{"\n".join([f"{key}:{graph}" for key,graph in CREDIT_ASSIST_GRAPHS.items()])}"
    )

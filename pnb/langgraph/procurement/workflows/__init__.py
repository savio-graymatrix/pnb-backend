from pnb import LOGGER, SETTINGS
import os
from pnb.langgraph.procurement.workflows.chatbot_graph import setup_chatbot_graph
from pnb.langgraph.procurement.workflows.query_graph import setup_query_graph
from pnb.langgraph.procurement.workflows.review_graph import setup_review_graph
from pnb.langgraph.procurement.workflows.mini_cb_graph import setup_mini_cb_graph
from pnb.langgraph.procurement.workflows.instruction_graph import setup_instruction_graph
from pnb.db.stores.MongoStore import MONGO_STORE
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver

PROCUREMENT_GRAPHS = dict()


async def compile_procurement_graphs():
    checkpointer = AsyncMongoDBSaver(MONGO_STORE.client,db_name=SETTINGS.DB_NAME)
    PROCUREMENT_GRAPHS.update(
        {
            "chatbot": await setup_chatbot_graph(checkpointer=checkpointer),
            "query": await setup_query_graph(checkpointer=checkpointer),
            "review": await setup_review_graph(checkpointer=checkpointer),
            "instruction": await setup_instruction_graph(checkpointer=checkpointer),
            "mini_cb": await setup_mini_cb_graph(checkpointer=checkpointer),
        }
    )
    for key, graph in PROCUREMENT_GRAPHS.items():
        os.makedirs(f"{os.getcwd()}/docs", exist_ok=True)
        os.makedirs(f"{os.getcwd()}/docs/images", exist_ok=True)
        graph.get_graph().draw_mermaid_png(output_file_path=f"docs/images/{key}.png")
    LOGGER.info(
        f"Procurement Graphs initialized:\n{"\n".join([f"{key}:{graph}" for key,graph in PROCUREMENT_GRAPHS.items()])}"
    )
 
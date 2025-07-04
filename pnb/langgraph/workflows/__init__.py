from pnb import LOGGER
import os
from pnb.langgraph.workflows.project_graph import setup_project_graph
from pnb.langgraph.workflows.credit_graph import setup_credit_graph
from pnb.langgraph.workflows.chatbot_graph import setup_chatbot_graph

GRAPHS = dict()


async def setup_graphs():
    GRAPHS.update(
        {
            "project": await setup_project_graph(),
            "credit": await setup_credit_graph(),
            "chatbot": await setup_chatbot_graph(),
        }
    )
    for key, graph in GRAPHS.items():
        os.makedirs(f"{os.getcwd()}/docs", exist_ok=True)
        os.makedirs(f"{os.getcwd()}/docs/images", exist_ok=True)
        graph.get_graph().draw_mermaid_png(output_file_path=f"docs/images/{key}.png")
    LOGGER.info(
        f"Graphs initialized:\n{"\n".join([f"{key}:{graph}" for key,graph in GRAPHS.items()])}"
    )

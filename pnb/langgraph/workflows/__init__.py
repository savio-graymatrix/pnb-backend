from pnb import LOGGER
import os

GRAPHS = dict()


async def setup_graphs():
    GRAPHS.update({})
    for key, graph in GRAPHS.items():
        os.makedirs(f"{os.getcwd()}/docs", exist_ok=True)
        os.makedirs(f"{os.getcwd()}/docs/images", exist_ok=True)
        graph.get_graph().draw_mermaid_png(output_file_path=f"docs/images/{key}.png")
    LOGGER.info(
        f"Graphs initialized:\n{"\n".join([f"{key}:{graph}" for key,graph in GRAPHS.items()])}"
    )

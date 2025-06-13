import os
from langgraph.graph.graph import CompiledGraph

def convert_to_png(graph: CompiledGraph, image_name: str = "graph") -> None:
    try:
        png_graph = graph.get_graph().draw_mermaid_png()
        path = os.path.join(f"{image_name}.png")
        with open(path, "wb") as f:
            f.write(png_graph)
            print(f"Saved graph as {image_name}.png")
    except Exception as e:
        print(f"Exception: {e}")


def load_data():
    pass

def save_file(filename: str, content: str):
    """Writes the content inside the filename, must be in .txt format

    Args:
        filename (str): The name of the file to write to
        content (str): The content to write to the file
    """
    with open(filename, "w") as f:
        f.write(content)
    
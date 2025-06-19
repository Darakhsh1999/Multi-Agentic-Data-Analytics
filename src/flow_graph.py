import os
from state import AgentState
from utils import convert_to_png
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from index_agent import index_agent
from manager_agent import route_agents
from data_clean_agent import data_clean_agent
import uuid







if __name__ == "__main__":



    uuid = uuid.uuid4()
    memory_path = os.path.join("..","memory",str(uuid))
    if not os.path.exists(memory_path):
        os.makedirs(memory_path)
    print(f"Initialized project with uuid: {uuid}")

    # Connstruct Graph
    graph = StateGraph(AgentState)

    # Add Nodes
    graph.add_node("agent_clean", data_clean_agent)
    graph.add_node("tool_clean", ToolNode(get_cleaning_tools))
    graph.add_node("index_agent", index_agent)
    graph.add_node("agent_manager", route_agents)
    graph.add_node("agent_analyze", lambda state: state)
    graph.add_node("agent_visualize", lambda state: state)
    graph.add_node("agent_write", lambda state: state)

    # Add Edges
    graph.set_entry_point("agent_clean")
    graph.add_edge("agent_clean", "index_agent")
    graph.add_edge("index_agent", "agent_manager")
    graph.add_conditional_edges(
        "agent_manager",
        route_agents,
        {
            "clean": "agent_clean",
            "analyze": "agent_analyze",
            "visualize": "agent_visualize",
            "write": "agent_write"
        }
    )

    # Compile Graph
    app = graph.compile()

    #convert_to_png(app, "graph_image")
    # Load in example file paths
    data_file = []
    path = os.path.abspath(os.path.join("..", "example-data"))
    print("Path: ", path)
    for root, dirs, files_ in os.walk(path):
        for file in files_:
            data_file.append(os.path.abspath(os.path.join(root, file)))
    print(f"Found {len(data_file)} files")

    state = AgentState(
        uploaded_file_paths=data_file,
        memory_path=memory_path
    )

    app.invoke(state)
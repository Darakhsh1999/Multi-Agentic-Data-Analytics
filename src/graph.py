from state import AgentState
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from index_agent import index_agent
from data_clean_agent import data_clean_agent
from langgraph.graph.graph import CompiledGraph


def create_graph() -> CompiledGraph:

    # Connstruct Graph
    graph = StateGraph(AgentState)

    # Add Nodes
    graph.add_node("agent_clean", data_clean_agent)
    graph.add_node("index_agent", index_agent)

    # Add Edges
    graph.set_entry_point("agent_clean")
    graph.add_edge("agent_clean", "index_agent")
    graph.set_finish_point("index_agent")

    # Compile Graph
    app = graph.compile()

    return app

from utils import convert_to_png
from langgraph.graph import StateGraph
from state import AgentState














# Connstruct Graph
graph = StateGraph(AgentState)

def temp(state: AgentState) -> AgentState:
    return state

# Add Nodes
graph.add_node("index_agent", temp)
graph.add_node("agent_clean", temp)
graph.add_node("agent_analyze", temp)
graph.add_node("agent_visualize", temp)
graph.add_node("agent_write", temp)
graph.add_node("agent_compiler", temp)

# Add Edges
graph.set_entry_point("agent_clean")
graph.add_edge("agent_clean", "agent_analyze")
graph.add_edge("agent_analyze", "agent_visualize")
graph.add_edge("agent_visualize", "agent_write")
graph.add_edge("agent_write", "agent_compiler")

# Compile Graph
app = graph.compile()

convert_to_png(app, "flow_graph")
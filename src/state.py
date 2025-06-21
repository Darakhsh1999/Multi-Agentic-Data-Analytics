from typing import Annotated, TypedDict, Dict, List, Any
from pathlib import Path
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
import uuid


class AgentState(TypedDict, total=False):
    """State for the data cleaning agent."""
    messages: Annotated[List[BaseMessage], add_messages]
    uuid: uuid.UUID
    memory_path: Path
    current_df: Any  # pd.DataFrame
    indexed: bool
    debug: int
from typing import TypedDict, Dict, List, Any
from pathlib import Path
import pandas as pd

class AgentState(TypedDict, total=False):
    """State for the data cleaning agent."""
    uploaded_file_paths: List[str]
    memory_path: Path
    current_df: Any  # Using Any to avoid Pydantic JSON schema issues with DataFrames
    output: str
    cleaned_file_paths: List[str]
    cleaned_dataframes: Dict[str, Any]  # Using Any for the same reason
    debug: int
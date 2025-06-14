from typing import TypedDict
from pathlib import Path


class AgentState(TypedDict):
    uploaded_file_paths: list[Path]
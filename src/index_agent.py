import os
import constants
from tqdm import tqdm
from state import AgentState
from utils import load_file_context
from agents import indexing_llm, FileContext
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)


def index_agent(state: AgentState) -> AgentState:

    if state["debug"] == 1:
        print(f"Entered index_agent")

    # Load in data files from memory path
    file_paths = []
    data_path = os.path.join(state["memory_path"], "data")
    for root, dirs, files_ in os.walk(data_path):
        for file in files_:
            file_paths.append(os.path.abspath(os.path.join(root, file)))
    
    if state["debug"] == 1:
        print(f"Found {len(file_paths)} files")

    content = ""
    for file_path in tqdm(file_paths):

        # Load in context and information about the file
        file_content = load_file_context(file_path)[:1000]
        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_path)[1]
        
        messages = [
            SystemMessage(content=constants.INDEX_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=f"Please index the content of the file: {file_name} with the following content:\n{file_content}")
        ]

        # Get the initial response
        response: FileContext = indexing_llm.invoke(messages)

        file_info = (
            f"File name: {file_name}\n"
            f"File type: {file_type}\n"
            f"File path: {file_path}\n"
            f"Description: {response.description}\n"
            f"Structure: {response.structure}\n"
            f"Metadata: {response.metadata}\n\n"
        )

        content += file_info

    try:
        index_file_path = os.path.join(state["memory_path"], "index.txt")
        with open(index_file_path, "w") as f:
            f.write(content)
    except Exception as e:
        print(f"Error writing to {index_file_path}: {str(e)}")

    state["indexed"] = True
    return state


if __name__ == "__main__":


    state = AgentState(
        uuid="3c6bb400-2ada-4681-90d3-d5d0ce12a67d",
        memory_path=os.path.join("runs", "3c6bb400-2ada-4681-90d3-d5d0ce12a67d"),
        debug=1
    )

    output_state = index_agent(state)



    
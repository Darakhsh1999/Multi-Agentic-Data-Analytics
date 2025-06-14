import os
from state import AgentState
from langchain_ollama import ChatOllama
from utils import load_file_data, save_file
from langchain_core.tools import tool
from langchain.agents.react.agent import create_react_agent
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)

from tqdm import tqdm


SYSTEM_PROMPT = """
You are an AI agent that will read in several data files typical of data analysis, ranging from pdf, xls, xlsx, doc, docx, txt, csv, etc. and create a single .txt index file with information about the available data.
You will be given a list of files to read in. You should store the following information about each file in the index file:
- The file name
- The file type
- The file size (in MB)
- A brief description of the data file
- Any potential structure of the data in the file, such as tables, images, etc.
- Any additional metadata about the file

You should write this information to the index file in the following format: "file name", "file type", "brief description", "file size".
Example
# "file name" - "file type" ("file size")
# Description: "brief description"
# Structure: "structure"
# Metadata: "metadata"

"""

# Index Agent Tools
tools = [
    save_file,
    load_file_data
]

model = ChatOllama(
    model="qwen3:8b",
    temperature=0,
).bind_tools(tools)


def index_agent(state: AgentState) -> AgentState:

    file_paths = state["uploaded_file_paths"]

    print(SYSTEM_PROMPT)

    response = model.invoke(
        input=[
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"The files you have access to are: {"\n".join(file_paths)}\n. Please create an index file.")
        ]
    )

    print(response.content)
    
    return state




if __name__ == "__main__":


    # Load in example file paths
    data_file = []
    path = os.path.abspath(os.path.join("..", "example-data"))
    print("Path: ", path)
    for root, dirs, files_ in os.walk(path):
        for file in files_:
            data_file.append(os.path.abspath(os.path.join(root, file)))
    from pprint import pprint
    print(f"Found {len(data_file)} files")

    state = AgentState(uploaded_file_paths=data_file)

    output_state = index_agent(state)



    
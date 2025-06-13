import os
from state import AgentState
from langchain_ollama import ChatOllama
from utils import save_file, load_data
from langchain_core.tools import tool

SYSTEM_PROMPT = """
You are an AI agent that will read in several data files, ranging from pdf, txt, csv, etc. and create a single .txt index file with information about the available data.
You will be given a list of files to read in.You should store the following information about each file in the index file:
    a brief description of the data file
    the number of lines in the file
    the number of words in the file
    the main topics in the file
    any key phrases or keywords in the file
    and the date the file was created
You should write this information to the index file in the following format: "file name", "file type", "brief description", "lines", "words", "main topics", "key phrases", "date created".
You should also store the contents of the file in a separate file with the same name as the original file but with a .txt extension.
"""

# Index Agent Tools
tools = [
    save_file,
    load_data
]

# model = ChatOllama(
#     model_name="llama3.2",
#     temperature=0.1,
# ).bind_tools(tools)


def index_agent(state: AgentState) -> AgentState:


    files = state["uploaded_files"]
    
    return state

from openai import OpenAI


# response = model.chat.completions.create(
#     model="llama3.2",
#     messages=[
#         {
#             "role": "system",
#             "content": SYSTEM_PROMPT
#         },
#         {
#             "role": "user",
#             "content": ""
#         }
#     ]
# )



if __name__ == "__main__":


    data_file = []
    for root, dirs, files_ in os.walk(os.path.join("..", "example-data")):
        for file in files_:
            data_file.append(os.path.join(root, file))
    from pprint import pprint
    pprint(data_file)



    
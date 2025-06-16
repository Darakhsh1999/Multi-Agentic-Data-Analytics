import os
from state import AgentState
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)
from tqdm import tqdm
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from utils import load_file_context, save_file

load_dotenv()


class FileContext(BaseModel):
    file_name: str = Field(description="The name of the file")
    file_type: str = Field(description="The type of the file")
    description: str = Field(description="A brief description of the file")
    structure: str = Field(description="The structure of the file if it is a table, image, etc. Keep it short and simple. For text files, just say typical text structure.")
    metadata: str = Field(description="Any additional metadata about the file if it is present inside the content")


SYSTEM_PROMPT = f"""
You are an AI assistant that will read in several data files typical of data analysis, such as pdf, xls, xlsx, doc, docx, txt, csv, etc. and create a single .txt index file with information about the available data.
You will be given the contents of a file in text format. You should store the following information about the file in the content below that is growing dynamically:
- The file name
- The file type
- A brief description of the data file
- Any potential structure of the data in the file, such as tables, images, etc. Keep this short and simple.
- Any additional metadata about the file if it is present inside the content. Keep this short and simple.

For each file, you should write this information to the index file in the following format:
# "file name" - "file type"
Path: "file path"
Description: "brief description"
Structure: "structure"
Metadata: "metadata"

Content:
{{content}}
"""

model = ChatOpenAI(
    model="gpt-4o-mini",
).with_structured_output(FileContext)

# model = init_chat_model(
#     model="qwen3:8b",
#     model_provider="ollama",
#     base_url="http://localhost:11434",
#     temperature=0
# ).with_structured_output(FileContext)

def index_agent(state: AgentState) -> AgentState:


    file_paths = state["uploaded_file_paths"]

    content = ""

    for file_path in tqdm(file_paths):


        file_content = load_file_context(file_path)[:1000]
        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_path)[1]
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT.format(content=content)),
            HumanMessage(content=f"Please index the content of the file: {file_name} with the following content:\n{file_content}")
        ]

        # Get the initial response
        response = model.invoke(input=messages)

        file_info = f"""
        # {file_name} - {file_type}
        Path: {file_path}
        Description: {response.description}
        Structure: {response.structure}
        Metadata: {response.metadata}
        """

        content += file_info

    save_file("index.txt", content)
    state["index_file_path"] = "index.txt"

    return state


if __name__ == "__main__":


    # Load in example file paths
    data_file = []
    path = os.path.abspath(os.path.join("..", "example-data"))
    print("Path: ", path)
    for root, dirs, files_ in os.walk(path):
        for file in files_:
            data_file.append(os.path.abspath(os.path.join(root, file)))
    print(f"Found {len(data_file)} files")

    state = AgentState(uploaded_file_paths=data_file)

    output_state = index_agent(state)



    
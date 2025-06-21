import time
import constants
from data_clean_agent_tools import get_cleaning_tools
from pydantic import BaseModel, Field
from ui_agent_tools import start_graph_workflow
from state import AgentState
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from dotenv import load_dotenv
load_dotenv()


## UI ##

ui_llm = init_chat_model(
    model="qwen3:4b",
    model_provider="ollama",
    base_url="http://localhost:11434",
    temperature=0.1,
    timeout=60
).bind_tools([start_graph_workflow])


## Data Cleaning ##

data_cleaning_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# Create the agent
agent_data_clean = create_react_agent(
    model=data_cleaning_llm,
    tools=get_cleaning_tools(),
    prompt=constants.DATA_CLEAN_AGENT_SYSTEM_PROMPT,
)


## Indexing ##

class FileContext(BaseModel):
    file_name: str = Field(description="The name of the file")
    file_type: str = Field(description="The type of the file")
    description: str = Field(description="A brief description of the file")
    structure: str = Field(description="The structure of the file if it is a table, image, etc. Keep it short and simple. For text files, just say typical text structure.")
    metadata: str = Field(description="Any additional metadata about the file if it is present inside the content. Keep it short and simple.")

use_openai = False

if use_openai:
    indexing_llm = ChatOpenAI(
        model="gpt-4o-mini",
    ).with_structured_output(FileContext)
else:
    indexing_llm = init_chat_model(
        model="qwen3:8b",
        model_provider="ollama",
        base_url="http://localhost:11434",
        temperature=0
    ).with_structured_output(FileContext)
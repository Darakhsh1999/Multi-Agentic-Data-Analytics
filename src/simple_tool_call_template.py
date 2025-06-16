from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)
from langchain_core.tools import tool




@tool
def addition(a: int, b: int) -> int:
    """Add two numbers together

    Args:
        a (int): First number
        b (int): Second number

    Returns:
        int: Sum of the two numbers
    """
    return a + b




model = init_chat_model(
    model="qwen3:8b",
    model_provider="ollama",
    base_url="http://localhost:11434",
    temperature=0
)

SYSTEM_PROMPT = """
You are an AI agent that will add two numbers together.
You will be given two numbers and you must add them together.
You must call the tools in order to access the file contents and metadata. The tools are accessed by calling a function with the same name as the tool. For example, to use the addition tool, you would call the addition() function.

"""

# Index Agent Tools
index_tools = [addition]


# Create a bound model with tools
bound_model = model.bind_tools(
    tools=index_tools,
)


if __name__ == "__main__":

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Add the numbers 2321 and 219001")
    ]

    # Get the initial response
    response = bound_model.invoke(input=messages)


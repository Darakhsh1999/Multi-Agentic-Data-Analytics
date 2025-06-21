import os
from tqdm import tqdm
from state import AgentState
from agents import agent_data_clean
from data_clean_agent_tools import load_tabular_data
from constants import DATA_CLEAN_AGENT_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage


def data_clean_agent(state: AgentState) -> AgentState:

    if state["debug"] == 1:
        print(f"Entered data_clean_agent")

    # Load in data files from memory path
    file_paths = []
    data_path = os.path.join(state["memory_path"], "data")
    for root, dirs, files_ in os.walk(data_path):
        for file in files_:
            file_paths.append(os.path.abspath(os.path.join(root, file)))

    tabular_formats = ["csv", "tsv", "xls", "xlsx"]

    # Filter out only tabular files
    tabular_files = list(filter(lambda x: x.split(".")[-1] in tabular_formats, file_paths))

    for file in tqdm(tabular_files, desc="Processing files"):

        # Load in data file
        df = load_tabular_data(file)
        state["current_df"] = df

        # Run agent with state
        agent_input = {
            "messages": [
                SystemMessage(content=DATA_CLEAN_AGENT_SYSTEM_PROMPT),
                HumanMessage(content=f"Please clean the data in the following file:\n{file}")
            ],
            "current_df": df, # Pass the current DataFrame to the agent
        }
        result = agent_data_clean.invoke(
            agent_input,
            debug=(True if state["debug"] == 1 else False)
        )
        print("REEEEEESULT", result)
        state.update(result)  # Update state with any changes from the agent

        # Save cleaned file
        cleaned_file_name = f"cleaned_{os.path.basename(file)}"
        cleaned_file_path = os.path.join(state["memory_path"], "data", cleaned_file_name)
        state["current_df"].to_csv(cleaned_file_path, index=False)

    return state


if __name__ == "__main__":

    # Example usage
    state = AgentState(
        uuid="3c6bb400-2ada-4681-90d3-d5d0ce12a67d",
        memory_path=os.path.join("runs", "3c6bb400-2ada-4681-90d3-d5d0ce12a67d"),
        debug=1
    )

    output_state = data_clean_agent(state)

    print(output_state)
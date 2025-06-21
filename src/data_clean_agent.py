import os
from tqdm import tqdm
from state import AgentState
from agents import agent_data_clean
from data_clean_agent_tools import load_tabular_data, set_dataframe, get_dataframe
from langchain.schema import HumanMessage

def data_clean_agent(state: AgentState) -> AgentState:

    if state["debug"]:
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
        set_dataframe(df)

        # Run agent with state
        print("INITIAL STATE", state)
        print(5*"\n")
        input("Press Enter to continue...")
        result = agent_data_clean.invoke(
            HumanMessage(content="Please clean the data by using the available tools."),
            config={"recursion_limit": 30},
            debug=(True if state["debug"] == 1 else False)
        )
        print(5*"\n")
        print("REEEEEESULT", result, type(result))
        print(5*"\n")
        state.update(result)  # Update state with any changes from the agent
        # Save cleaned file
        cleaned_file_name = f"cleaned_{os.path.basename(file)}"
        cleaned_file_path = os.path.join(state["memory_path"], "output", cleaned_file_name)
        cleaned_df = get_dataframe()
        cleaned_df.to_csv(cleaned_file_path, index=False)

    return state


if __name__ == "__main__":

    # Example usage
    state = AgentState(
        messages=[],
        uuid="6cf67e12-87ce-4135-88c8-08845f4812f5",
        memory_path=os.path.join("runs", "6cf67e12-87ce-4135-88c8-08845f4812f5"),
        debug=1,
    )

    output_state = data_clean_agent(state)

    print(output_state)
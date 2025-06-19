import os
from state import AgentState
import pandas as pd
from pathlib import Path
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from typing import Optional, Dict, List
from langchain_openai import ChatOpenAI
from typing import Dict, List, Optional, Union
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are an expert data cleaning assistant. Your task is to analyze the provided data sample and 
clean it using the available tools. Tasks such as renaming columns, dropping columns, removing 
duplicates, converting data types of columns, and handling missing values are available and expected tasks.
"""

def load_tabular_data(file_path: Union[str, Path]) -> pd.DataFrame:

    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    try:
        if suffix == '.csv':
            return pd.read_csv(file_path)
        elif suffix == '.tsv':
            return pd.read_csv(file_path, sep='\t')
        elif suffix in ['.xls', '.xlsx']:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    except Exception as e:
        raise Exception(f"Error loading file {file_path}: {str(e)}")


## TOOLS ##
@tool
def table_head(state: AgentState, n: int = 5) -> AgentState:
    """Return the first n rows of the current DataFrame.
    
    Args:
        state: The current agent state
        n: Number of rows to return (default: 5)
        
    Returns:
        Updated agent state with the result in the 'output' field
    """
    df = state.get('current_df')
    if df is not None:
        state['output'] = df.head(n).to_json(orient='records', indent=2)
    else:
        state['output'] = "No DataFrame loaded in state"
    return state


@tool
def table_tail(state: AgentState, n: int = 5) -> AgentState:
    """Return the last n rows of the current DataFrame.
    
    Args:
        state: The current agent state
        n: Number of rows to return (default: 5)
        
    Returns:
        Updated agent state with the result in the 'output' field
    """
    df = state.get('current_df')
    if df is not None:
        state['output'] = df.tail(n).to_json(orient='records', indent=2)
    else:
        state['output'] = "No DataFrame loaded in state"
    return state


@tool
def table_info(state: AgentState) -> AgentState:
    """Return information about the current DataFrame.
    
    Args:
        state: The current agent state
        
    Returns:
        Updated agent state with DataFrame info in the 'output' field
    """
    df = state.get('current_df')
    if df is not None:
        info_dict = {
            'dtypes': df.dtypes.astype(str).to_dict(),
            'columns': list(df.columns),
            'shape': {'rows': len(df), 'columns': len(df.columns)},
            'null_counts': df.isnull().sum().to_dict()
        }
        state['output'] = json.dumps(info_dict, indent=2)
    else:
        state['output'] = "No DataFrame loaded in state"
    return state

@tool
def table_describe(state: AgentState) -> AgentState:
    """Return a statistical description of the current DataFrame.
    
    Args:
        state: The current agent state
        
    Returns:
        Updated agent state with statistical description in the 'output' field
    """
    df = state.get('current_df')
    if df is not None:
        state['output'] = df.describe().to_json(orient='index', indent=2)
    else:
        state['output'] = "No DataFrame loaded in state"
    return state


@tool
def rename_columns(state: AgentState, column_mapping: Dict[str, str]) -> AgentState:
    """Rename columns in the current DataFrame.
    
    Args:
        state: The current agent state
        column_mapping: Dictionary mapping old column names to new column names
        
    Returns:
        Updated agent state with renamed columns and status message
    """
    df = state.get('current_df')
    if df is not None:
        state['current_df'] = df.rename(columns=column_mapping)
        state['output'] = f"Renamed columns: {column_mapping}"
    else:
        state['output'] = "No DataFrame loaded in state"
    return state


@tool
def drop_columns(state: AgentState, columns: List[str]) -> AgentState:
    """Drop specified columns from the current DataFrame.
    
    Args:
        state: The current agent state
        columns: List of column names to drop
        
    Returns:
        Updated agent state with columns dropped and status message
    """
    df = state.get('current_df')
    if df is not None:
        valid_columns = [col for col in columns if col in df.columns]
        if valid_columns:
            state['current_df'] = df.drop(columns=valid_columns, errors='ignore')
            state['output'] = f"Dropped columns: {valid_columns}"
        else:
            state['output'] = "No valid columns to drop"
    else:
        state['output'] = "No DataFrame loaded in state"
    return state


@tool
def remove_duplicates(state: AgentState, subset: Optional[List[str]] = None) -> AgentState:
    """Remove duplicate rows from the current DataFrame.
    
    Args:
        state: The current agent state
        subset: List of column names to consider when identifying duplicates
               If None, all columns are used
               
    Returns:
        Updated agent state with duplicates removed and status message
    """
    df = state.get('current_df')
    if df is not None:
        initial_count = len(df)
        state['current_df'] = df.drop_duplicates(subset=subset)
        removed_count = initial_count - len(state['current_df'])
        state['output'] = f"Removed {removed_count} duplicate rows"
    else:
        state['output'] = "No DataFrame loaded in state"
    return state


@tool
def convert_column_type(state: AgentState, column: str, target_type: str) -> AgentState:
    """Convert a column to a specified data type in the current DataFrame.
    
    Args:
        state: The current agent state
        column: Name of the column to convert
        target_type: Target data type ('numeric', 'datetime', 'category')
        
    Returns:
        Updated agent state with converted column and status message
    """
    df = state.get('current_df')
    if df is None:
        state['output'] = "No DataFrame loaded in state"
        return state
        
    if column not in df.columns:
        state['output'] = f"Column '{column}' not found in DataFrame"
        return state
        
    try:
        original_dtype = str(df[column].dtype)
        if target_type == 'datetime':
            df[column] = pd.to_datetime(df[column], errors='coerce')
        elif target_type == 'numeric':
            df[column] = pd.to_numeric(df[column], errors='coerce')
        elif target_type == 'category':
            df[column] = df[column].astype('category')
        
        new_dtype = str(df[column].dtype)
        state['current_df'] = df
        state['output'] = f"Converted column '{column}' from {original_dtype} to {new_dtype}"
    except Exception as e:
        state['output'] = f"Failed to convert column '{column}' to {target_type}: {str(e)}"
    
    return state


@tool
def handle_missing_values(state: AgentState, column: str, strategy: str) -> AgentState:
    """Handle missing values in a column of the current DataFrame.
    
    Args:
        state: The current agent state
        column: Name of the column to process
        strategy: Strategy to handle missing values:
                 'drop' - Drop rows with missing values in this column
                 'mean' - Fill with column mean (numeric only)
                 'median' - Fill with column median (numeric only)
                 'mode' - Fill with most common value
                 'ffill' - Forward fill
                 'bfill' - Backward fill
                 
    Returns:
        Updated agent state with missing values handled and status message
    """
    df = state.get('current_df')
    if df is None:
        state['output'] = "No DataFrame loaded in state"
        return state
        
    if column not in df.columns:
        state['output'] = f"Column '{column}' not found in DataFrame"
        return state
    
    initial_missing = df[column].isna().sum()
    if initial_missing == 0:
        state['output'] = f"No missing values found in column '{column}'"
        return state
    
    try:
        if strategy == 'drop':
            state['current_df'] = df.dropna(subset=[column])
            state['output'] = f"Dropped {initial_missing} rows with missing values in column '{column}'"
            
        elif strategy == 'mean' and pd.api.types.is_numeric_dtype(df[column]):
            fill_value = df[column].mean()
            df[column] = df[column].fillna(fill_value)
            state['output'] = f"Filled {initial_missing} missing values in column '{column}' with mean: {fill_value:.2f}"
            
        elif strategy == 'median' and pd.api.types.is_numeric_dtype(df[column]):
            fill_value = df[column].median()
            df[column] = df[column].fillna(fill_value)
            state['output'] = f"Filled {initial_missing} missing values in column '{column}' with median: {fill_value:.2f}"
            
        elif strategy == 'mode':
            mode_values = df[column].mode()
            if not mode_values.empty:
                fill_value = mode_values[0]
                df[column] = df[column].fillna(fill_value)
                state['output'] = f"Filled {initial_missing} missing values in column '{column}' with mode: {fill_value}"
            else:
                state['output'] = f"No mode available for column '{column}'. No changes made."
                
        elif strategy == 'ffill':
            df[column] = df[column].fillna(method='ffill')
            filled = initial_missing - df[column].isna().sum()
            state['output'] = f"Forward filled {filled} missing values in column '{column}'"
            
        elif strategy == 'bfill':
            df[column] = df[column].fillna(method='bfill')
            filled = initial_missing - df[column].isna().sum()
            state['output'] = f"Backward filled {filled} missing values in column '{column}'"
            
        else:
            state['output'] = f"Invalid strategy '{strategy}' for column '{column}'. No changes made."
        
    except Exception as e:
        state['output'] = f"Error handling missing values in column '{column}': {str(e)}"
    
    return state


def get_cleaning_tools() -> list:
    """Return a list of all available cleaning tools."""
    return [
        rename_columns,
        drop_columns,
        remove_duplicates,
        convert_column_type,
        handle_missing_values,
        table_head,
        table_tail,
        table_info
    ]


def data_clean_agent(state: AgentState) -> AgentState:

    if state["debug"] == 1:
        print(f"Entered data_clean_agent")

    tabular_formats = ["csv", "tsv", "xls", "xlsx"]

    # Filter out only tabular files
    tabular_files = list(filter(lambda x: x.split(".")[-1] in tabular_formats, state["uploaded_file_paths"]))

    if use_openai:
        model = ChatOpenAI(
            model="gpt-4",
            temperature=0
        )
    else:
        model = init_chat_model(
            model="qwen3:8b",
            model_provider="ollama",
            base_url="http://localhost:11434",
            temperature=0
        )

    # Create the agent
    agent = create_react_agent(
        model=model,
        tools=get_cleaning_tools(),
        prompt=SYSTEM_PROMPT,
        debug=True
    )


    for file in tqdm(tabular_files, desc="Processing files"):

        # Load in data file
        df = load_tabular_data(file)

        state["current_df"] = df

        # Run agent with state
        result = agent.invoke(
            {
                "messages": [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=f"Please clean the data in the following file:\n{file}")
                ],
                **state  # Pass the current state to the agent
            },
            debug=True
        )
        state.update(result)  # Update state with any changes from the agent

        # Save cleaned file
        file_name = os.path.basename(file)
        cleaned_file_name = f"cleaned_{file_name}"
        cleaned_file_path = os.path.join(state["temp_dir"], cleaned_file_name)
        state["current_df"].to_csv(cleaned_file_path, index=False)
        state["cleaned_file_paths"].append(cleaned_file_path)
        state["cleaned_dataframes"][cleaned_file_name] = state["current_df"]

    return state

if __name__ == "__main__":

    use_openai = False

    csv_data = os.listdir(os.path.join("..","example-data","csv"))
    csv_data = [os.path.join("..","example-data","csv",f) for f in csv_data]

    # Example usage
    test_state = AgentState(
        uploaded_file_paths=csv_data,
        debug=1
    )

    result_state = data_clean_agent(test_state)
    print("\nCleaned files:", result_state["cleaned_file_paths"])
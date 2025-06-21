import json
from typing import Any
from pathlib import Path
from typing import Dict, List, Optional, Union
from langchain_core.tools import tool
# State management is now handled by the agent

## Functions ##

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
def table_head(current_df: Any, n: int = 5) -> str:
    """Return the first n rows of the current DataFrame.
    
    Args:
        current_df: The current DataFrame
        n: Number of rows to return (default: 5)
        
    Returns:
        Updated agent state with the result in the 'output' field
    """
    if current_df is not None:
        return current_df.head(n).to_json(orient='records', indent=2)
    else:
        return "No DataFrame loaded in state"


@tool
def table_tail(current_df: Any, n: int = 5) -> str:
    """Return the last n rows of the current DataFrame.
    
    Args:
        current_df: The current DataFrame
        n: Number of rows to return (default: 5)
        
    Returns:
        JSON string containing the last n rows of the DataFrame
    """
    if current_df is not None:
        return current_df.tail(n).to_json(orient='records', indent=2)
    else:
        return "No DataFrame loaded in state"


@tool
def table_info(current_df: Any) -> str:
    """Return information about the current DataFrame.
    
    Args:
        current_df: The current DataFrame
        
    Returns:
        JSON string containing DataFrame information
    """
    if current_df is not None:
        info_dict = {
            'dtypes': current_df.dtypes.astype(str).to_dict(),
            'columns': list(current_df.columns),
            'shape': {'rows': len(current_df), 'columns': len(current_df.columns)},
            'null_counts': current_df.isnull().sum().to_dict()
        }
        return json.dumps(info_dict, indent=2)
    else:
        return "No DataFrame loaded in state"

@tool
def table_describe(current_df: Any) -> str:
    """Return a statistical description of the current DataFrame.
    
    Args:
        current_df: The current DataFrame
        
    Returns:
        JSON string containing statistical description of the DataFrame
    """
    if current_df is not None:
        return current_df.describe().to_json(orient='index', indent=2)
    else:
        return "No DataFrame loaded in state"


@tool
def rename_columns(current_df: Any, column_mapping: Dict[str, str]) -> str:
    """Rename columns in the current DataFrame.
    
    Args:
        current_df: The current DataFrame
        column_mapping: Dictionary mapping old column names to new column names
        
    Returns:
        Status message and the updated DataFrame
    """
    if current_df is not None:
        current_df.rename(columns=column_mapping, inplace=True)
        return f"Renamed columns: {column_mapping}"
    else:
        return "No DataFrame loaded in state"


@tool
def drop_columns(current_df: Any, columns: List[str]) -> str:
    """Drop specified columns from the current DataFrame.
    
    Args:
        current_df: The current DataFrame
        columns: List of column names to drop
        
    Returns:
        Status message and the updated DataFrame
    """
    if current_df is not None:
        valid_columns = [col for col in columns if col in current_df.columns]
        if valid_columns:
            current_df.drop(columns=valid_columns, errors='ignore', inplace=True)
            return f"Dropped columns: {valid_columns}"
        else:
            return "No valid columns to drop"
    else:
        return "No DataFrame loaded in state"


@tool
def remove_duplicates(current_df: Any, subset: Optional[List[str]] = None) -> str:
    """Remove duplicate rows from the current DataFrame.
    
    Args:
        current_df: The current DataFrame
        subset: List of column names to consider when identifying duplicates
               If None, all columns are used
               
    Returns:
        Status message and the updated DataFrame
    """
    if current_df is not None:
        initial_count = len(current_df)
        current_df.drop_duplicates(subset=subset, inplace=True)
        removed_count = initial_count - len(current_df)
        return f"Removed {removed_count} duplicate rows"
    else:
        return "No DataFrame loaded in state"


@tool
def convert_column_type(current_df: Any, column: str, target_type: str) -> str:
    """Convert a column to a specified data type in the current DataFrame.
    
    Args:
        current_df: The current DataFrame
        column: Name of the column to convert
        target_type: Target data type ('numeric', 'datetime', 'category')
        
    Returns:
        Status message and the updated DataFrame
    """
    if current_df is None:
        return "No DataFrame loaded in state"
        
    if column not in current_df.columns:
        return f"Column '{column}' not found in DataFrame"
        
    try:
        original_dtype = str(current_df[column].dtype)
        if target_type == 'datetime':
            current_df[column] = pd.to_datetime(current_df[column], errors='coerce')
        elif target_type == 'numeric':
            current_df[column] = pd.to_numeric(current_df[column], errors='coerce')
        elif target_type == 'category':
            current_df[column] = current_df[column].astype('category')
        else:
            return f"Unsupported target type: {target_type}"
        
        new_dtype = str(current_df[column].dtype)
        return f"Converted column '{column}' from {original_dtype} to {new_dtype}"
    except Exception as e:
        return f"Failed to convert column '{column}' to {target_type}: {str(e)}"


@tool
def handle_missing_values(current_df: Any, column: str, strategy: str) -> str:
    """Handle missing values in a column of the current DataFrame.
    
    Args:
        current_df: The current DataFrame
        column: Name of the column to process
        strategy: Strategy to handle missing values:
                 'drop' - Drop rows with missing values in this column
                 'mean' - Fill with column mean (numeric only)
                 'median' - Fill with column median (numeric only)
                 'mode' - Fill with most common value
                 'ffill' - Forward fill
                 'bfill' - Backward fill
                 
    Returns:
        Status message and the updated DataFrame
    """
    if current_df is None:
        return "No DataFrame loaded in state"
        
    if column not in current_df.columns:
        return f"Column '{column}' not found in DataFrame"
    
    initial_missing = df[column].isna().sum()
    if initial_missing == 0:
        return f"No missing values found in column '{column}'"
    
    try:
        if strategy == 'drop':
            current_df.dropna(subset=[column], inplace=True)
            return f"Dropped {initial_missing} rows with missing values in column '{column}'"
            
        elif strategy == 'mean' and pd.api.types.is_numeric_dtype(current_df[column]):
            fill_value = current_df[column].mean()
            current_df[column] = current_df[column].fillna(fill_value)
            return f"Filled {initial_missing} missing values in column '{column}' with mean: {fill_value:.2f}"
            
        elif strategy == 'median' and pd.api.types.is_numeric_dtype(current_df[column]):
            fill_value = current_df[column].median()
            current_df[column] = current_df[column].fillna(fill_value)
            return f"Filled {initial_missing} missing values in column '{column}' with median: {fill_value:.2f}"
            
        elif strategy == 'mode':
            mode_values = current_df[column].mode()
            if not mode_values.empty:
                fill_value = mode_values[0]
                df[column] = df[column].fillna(fill_value)
                return f"Filled {initial_missing} missing values in column '{column}' with mode: {fill_value}"
            else:
                return f"No mode available for column '{column}'. No changes made."
                
        elif strategy == 'ffill':
            current_df[column] = current_df[column].fillna(method='ffill')
            filled = initial_missing - current_df[column].isna().sum()
            return f"Forward filled {filled} missing values in column '{column}'"
            
        elif strategy == 'bfill':
            current_df[column] = current_df[column].fillna(method='bfill')
            filled = initial_missing - current_df[column].isna().sum()
            return f"Backward filled {filled} missing values in column '{column}'"
            
        else:
            return f"Invalid strategy '{strategy}' for column '{column}'. No changes made."
        
    except Exception as e:
        return f"Error handling missing values in column '{column}': {str(e)}"


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
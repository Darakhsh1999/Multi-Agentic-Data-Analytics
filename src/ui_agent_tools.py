from datetime import datetime
from langchain_core.tools import tool

@tool
def start_graph_workflow() -> dict[str, str]:
    """Initialize and start the graph workflow.
    
    This function serves as a trigger point for starting a graph workflow process.
    When called, it returns a success status with a timestamp, which can be used
    to verify that the workflow has been properly initialized.
    
    Returns:
        dict[str, str]: A dictionary containing:
            - status (str): Indicates the success/failure of the operation
            - message (str): Human-readable message about the operation status
            - timestamp (str): ISO 8601 formatted timestamp of when the workflow was started
            
    Example:
        >>> start_graph_workflow()
        {
            'status': 'success',
            'message': 'Graph workflow has been successfully initialized and started',
            'timestamp': '2025-06-20T10:10:28.123456'
        }
    """
    return {
        "status": "success",
        "message": "Graph workflow has been successfully initialized and started",
        "timestamp": datetime.now().isoformat()
    }


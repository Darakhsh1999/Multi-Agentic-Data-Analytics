import os
import uuid
import graph
import constants
import os.path as osp
import streamlit as st
from state import AgentState
from typing import List, Tuple
from agents import ui_llm
from langgraph.graph.graph import CompiledGraph
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    AIMessage,
    ToolMessage
)

# Initialize session state
if 'uuid' not in st.session_state:
    uuid = str(uuid.uuid4())
    os.makedirs(osp.join('runs', uuid, "data"))
    os.makedirs(osp.join('runs', uuid, "logs"))
    os.makedirs(osp.join('runs', uuid, "output"))
    st.session_state.uuid = uuid

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files: List[Tuple[str, bytes]] = []  # List of (filename, file content)

if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
    
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False

if 'chat_history' not in st.session_state:
    st.session_state.chat_history: List[Tuple[str, str]] = []  # List of (role, message)

if "agent_state" not in st.session_state:
    st.session_state.agent_state = AgentState(
        uuid=st.session_state.uuid,
        messages=[],
        debug=True,
        memory_path=osp.join('runs', st.session_state.uuid)
    )

def invoke_llm() -> BaseMessage | CompiledGraph:
    """Invoke the LLM with the given prompt."""

    # Get chat history
    chat_history: List[BaseMessage] = st.session_state.agent_state["messages"]
    chat_history[-1].content += "/nothink"

    # Call the UI agent
    response = ui_llm.invoke([SystemMessage(content=constants.UI_AGENT_SYSTEM_PROMPT)] + chat_history)

    # Check if tool call (e.g. start_graph_workflow)
    if response.tool_calls:

        for tool_call in response.tool_calls:

            st.session_state.chat_history.append(("tool", f"Called tool: {tool_call["name"]} with args: {tool_call["args"]}")) # For streamlit rendering
            st.session_state.agent_state["messages"].append(ToolMessage(
                content=response.content,
                name=tool_call["name"],
                tool_call_id=tool_call["id"]
            )) # For agent processing
        
        # Render tool call
        with st.chat_message("tool", avatar="🛠️"):
            st.markdown(
                f"""
                <div style="border-radius: 0.5rem; border: 1px solid #ccc; padding: 0.5rem; margin: 0.5rem 0">
                    {f"Called tool: {tool_call["name"]} with args: {tool_call["args"]}"}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        return graph.create_graph()

    else: # Regular response  
        return response
        

def handle_file_upload(uploaded_files) -> None:
    """Store uploaded files in memory, avoiding duplicates.
    
    Args:
        uploaded_files: List of files uploaded through st.file_uploader
    """
    if uploaded_files:
        current_filenames = {filename for filename, _ in st.session_state.uploaded_files}
        
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in current_filenames:
                st.session_state.uploaded_files.append((uploaded_file.name, uploaded_file.getvalue()))
    
    st.session_state.uploader_key += 1  # Force widget reset

def clear_files() -> None:
    """Clear all uploaded files."""
    st.session_state.uploaded_files.clear()
    st.session_state.uploader_key += 1

# Main UI
st.title("Data Cleaning Agent 🧹")

# Main area shows either uploader or chat interface
if st.session_state.show_chat:

    # Render chat history
    for role, message in st.session_state.chat_history:
        if role == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message)
        elif role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(message)
        elif role == "tool":
            with st.chat_message("tool", avatar="🛠️"):
                st.markdown(
                    f"""
                    <div style="border-radius: 0.5rem; border: 1px solid #ccc; padding: 0.5rem; margin: 0.5rem 0">
                        {message}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    # Process user input
    if (query := st.chat_input("Ask anything...")):

        # Add user query to chat history
        st.session_state.chat_history.append(("user", query)) # For streamlit rendering
        st.session_state.agent_state["messages"].append(HumanMessage(content=query)) # For agent processing

        with st.chat_message("user", avatar="👤"):
            st.markdown(query)

        # Invoke UI agent
        try:

            response = invoke_llm()

            if isinstance(response, BaseMessage): # Regular message
                st.session_state.chat_history.append(("assistant", response.content))
                st.session_state.agent_state["messages"].append(AIMessage(content=response.content)) # For agent processing
                st.rerun()
            elif isinstance(response, CompiledGraph): # Compiled graph

                # Write uploaded file to memory
                for filename, file_content in st.session_state.uploaded_files:
                    with open(os.path.join(st.session_state.agent_state["memory_path"], "data", filename), "wb") as f:
                        f.write(file_content)

                compiled_graph: CompiledGraph = response
                result: AgentState = compiled_graph.invoke(st.session_state.agent_state)
                st.session_state.agent_state = result
                # TODO update chat history with tool calls and agent responses
            else:
                print(f"Unknown response type: {type(response)}")
                
        except Exception as e:
            print(f"Error invoking UI agent: {e}")
            response = "Error invoking UI agent, try again."

else:
    # Show uploader when not in chat mode
    uploaded_files = st.file_uploader(
        label="Drag & drop files or click browse to select files to add",
        accept_multiple_files=True,
        key=f"file_uploader_{st.session_state.uploader_key}",
        help="Upload one or more files to clean"
    )

    # Handle new file uploads
    if uploaded_files:
        handle_file_upload(uploaded_files)
        st.rerun()

    if st.session_state.uploaded_files:
        st.success(f"✅ {len(st.session_state.uploaded_files)} file(s) ready for processing")
        if st.button("Start Processing", type="primary"):
            st.session_state.show_chat = True
            st.session_state.chat_history.append(("assistant", "Hello! I am a data cleaning agent ready to help you analyze and clean you data files. Do you have any requirements for the data cleaning or should I initialize the cleaning process?"))
            st.rerun()
    else:
        st.info("Upload files using the uploader above. View and manage files in the sidebar.")

# Sidebar with file list and controls
with st.sidebar:
    st.markdown("<h3 style='font-size: 1.1em;'>Uploaded Files</h3>", unsafe_allow_html=True)
    
    # File list with fixed height and scroll
    if st.session_state.uploaded_files:
        # Add CSS for the file list
        st.markdown("""
        <style>
        .file-list-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 8px;
            margin: 10px 0;
        }
        .file-item {
            padding: 6px 0;
            border-bottom: 1px solid #f0f0f0;
            font-family: monospace;
            font-size: 0.9em;
            word-break: break-all;
        }
        .file-item:last-child {
            border-bottom: none;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create a fixed height container for the file list
        with st.container():
            # Use markdown with HTML for the scrollable list
            file_items = '\n'.join(
                f'<div class="file-item">{filename}</div>'
                for filename, _ in st.session_state.uploaded_files
            )
            st.markdown(
                f'<div class="file-list-container">{file_items}</div>',
                unsafe_allow_html=True
            )
        
        # Show Clear All button only when not in chat mode
        if not st.session_state.show_chat:
            if st.button("Clear All", type="secondary"):
                clear_files()
                st.rerun()
    else:
        st.info("No files uploaded yet")
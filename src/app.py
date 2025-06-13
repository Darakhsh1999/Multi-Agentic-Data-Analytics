import streamlit as st
from pathlib import Path
from typing import Dict, List, Tuple
import tempfile

# Initialize session state
if 'file_paths' not in st.session_state:
    st.session_state.file_paths: Dict[str, str] = {}  # filename -> filepath

if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
    
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False

if 'chat_history' not in st.session_state:
    st.session_state.chat_history: List[Tuple[str, str]] = []  # List of (role, message)

# Create temp directory for uploaded files
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = Path(tempfile.mkdtemp(prefix="doc_chat_"))
    st.session_state.temp_dir.mkdir(exist_ok=True)

def handle_file_upload(files) -> None:
    """Save uploaded files and store their paths."""
    for file in files:
        if file.name not in st.session_state.file_paths:
            # Save to temp location
            temp_path = st.session_state.temp_dir / file.name
            with open(temp_path, "wb") as f_out:
                f_out.write(file.getvalue())
            st.session_state.file_paths[file.name] = str(temp_path.absolute())
        st.session_state.uploader_key += 1  # Force widget reset

def clear_files() -> None:
    """Clear all uploaded files."""
    for filepath in st.session_state.file_paths.values():
        try:
            Path(filepath).unlink(missing_ok=True)
        except Exception as e:
            st.error(f"Error deleting {filepath}: {e}")
    st.session_state.file_paths.clear()
    st.session_state.uploader_key += 1

# Main UI
st.title("Document Chat Interface")

# File uploader
uploaded_files = st.file_uploader(
    "Drag & drop files or click to browse",
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.uploader_key}",
    help="Upload one or more files to analyze"
)

# Handle new file uploads
if uploaded_files:
    handle_file_upload(uploaded_files)
    st.rerun()

# Main area shows either uploader or chat interface
if st.session_state.show_chat:
    # Show chat interface
    st.success(f"💬 Chat Interface - {len(st.session_state.file_paths)} file(s) loaded")
    
    # Display chat history
    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(message)
    
    # Chat input
    if prompt := st.chat_input("Ask about your files..."):
        st.session_state.chat_history.append(("user", prompt))
        # Add a placeholder response
        st.session_state.chat_history.append(("assistant", "Processing your question about the files..."))
        st.rerun()
else:
    # Show uploader
    if st.session_state.file_paths:
        st.success(f"✅ {len(st.session_state.file_paths)} file(s) ready for processing")
    else:
        st.info("Upload files using the uploader above. View and manage files in the sidebar.")

# Sidebar with file list and controls
with st.sidebar:
    st.markdown("<h3 style='font-size: 1.1em;'>Uploaded Files</h3>", unsafe_allow_html=True)
    
    # File list with fixed height and scroll
    if st.session_state.file_paths:
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
                for filename in st.session_state.file_paths
            )
            st.markdown(
                f'<div class="file-list-container">{file_items}</div>',
                unsafe_allow_html=True
            )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear All", type="secondary"):
                clear_files()
                st.rerun()
        with col2:
            if st.button("Start Processing", type="primary"):
                st.session_state.show_chat = True
                st.session_state.chat_history.append(("assistant", f"I'm ready to help you analyze {len(st.session_state.file_paths)} file(s). What would you like to know?"))
                st.rerun()
    else:
        st.info("No files uploaded yet")
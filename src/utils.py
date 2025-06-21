import os
import pandas as pd
from langgraph.graph.graph import CompiledGraph
from pathlib import Path
from PyPDF2 import PdfReader
from docx import Document
from typing import Union

def convert_to_png(graph: CompiledGraph, image_name: str = "graph") -> None:
    try:
        png_graph = graph.get_graph().draw_mermaid_png()
        path = os.path.join(f"{image_name}.png")
        with open(path, "wb") as f:
            f.write(png_graph)
            print(f"Saved graph as {image_name}.png")
    except Exception as e:
        print(f"Exception: {e}")


def load_file_context(file_path: Union[str, os.PathLike]) -> str:
    """Load and process file data into a text string for LLM context.

    Args:
        file_path (Union[str, os.PathLike]): Path to the file to be loaded

    Returns:
        str: Text content of the file or an error message
    """

    try:
        # Convert to Path object for better path handling
        path = Path(file_path)
        
        # Check if file exists and is accessible
        if not path.exists():
            return f"Error: File not found: {file_path}"
            
        if not path.is_file():
            return f"Error: Path is not a file: {file_path}"
            
        # Get file extension in lowercase for case-insensitive comparison
        file_ext = path.suffix.lower()[1:]  # Remove the dot
        
        # Text-based files
        if file_ext in ['txt']:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
                
        # Word documents
        elif file_ext in ['docx']:
            try:
                doc = Document(path)
                return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            except Exception as e:
                return f"Error reading Word document: {str(e)}"
                
        # PDF files
        elif file_ext == 'pdf':
            try:
                with open(path, 'rb') as f:
                    reader = PdfReader(f)
                    text = []
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text.append(page_text)
                    return '\n'.join(text) if text else "No extractable text found in PDF"
            except Exception as e:
                return f"Error reading PDF: {str(e)}"
                
        # Spreadsheet files
        elif file_ext in ['csv', 'xls', 'xlsx']:
            try:
                if file_ext == 'csv':
                    df = pd.read_csv(path)
                else:  # xls or xlsx
                    df = pd.read_excel(path)
                # Convert to string representation with tab separation
                return df.to_string(index=False)
            except Exception as e:
                return f"Error processing spreadsheet: {str(e)}"
                
        # Image files
        elif file_ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg']:
            # For images, we can't extract text, but can provide metadata
            try:
                file_stats = os.stat(path)
                return (
                    f"Image file detected. "
                    f"Size: {file_stats.st_size / 1024:.2f} KB, "
                    f"Last modified: {file_stats.st_mtime}"
                )
            except Exception as e:
                return f"Error reading image metadata: {str(e)}"
                
        # Unsupported file types
        else:
            return f"Unsupported file type: {file_ext}"
            
    except PermissionError:
        return f"Error: Permission denied when accessing {file_path}"
    except Exception as e:
        return f"Error processing file {file_path}: {str(e)}"
    
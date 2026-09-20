# tools/custom_tools.py
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from config import get_allowed_directory


class ReadFileInput(BaseModel):
    target: str = Field(
        description="The filename (e.g., 'config.json') or path to search for and read within the allowed directory."
    )


@tool("read_file", args_schema=ReadFileInput)
def read_file(target: str) -> str:
    """Searches for a file by name or path within the allowed root directory and returns its text contents."""
    try:
        allowed_dir = get_allowed_directory()
        target_path = Path(target)
        
        # 1. Direct Path Lookup
        resolved_direct = (allowed_dir / target_path).resolve() if not target_path.is_absolute() else target_path.resolve()
        
        if resolved_direct.exists() and resolved_direct.is_file():
            if not resolved_direct.is_relative_to(allowed_dir):
                return f"Error: Access denied. '{target}' is outside allowed directory."
            return resolved_direct.read_text(encoding="utf-8")

        # 2. Recursive Search
        search_filename = target_path.name
        matching_files = [f for f in allowed_dir.rglob(search_filename) if f.is_file()]

        if not matching_files:
            return f"Error: No file named '{target}' found anywhere in '{allowed_dir}'."

        if len(matching_files) > 1:
            matches_list = "\n".join([f"- {f.relative_to(allowed_dir)}" for f in matching_files])
            return f"Multiple files matching '{target}' were found:\n{matches_list}\nPlease specify the exact path."

        found_file = matching_files[0]
        return found_file.read_text(encoding="utf-8")

    except Exception as e:
        return f"Error reading file '{target}': {str(e)}"

class WriteFileInput(BaseModel):
    target: str = Field(
        description="The filename (e.g., 'config.json') or path to write to within the allowed directory."
    )
    content: str = Field(
        description="The content to write to the specified file."
    )

@tool("write_file", args_schema=WriteFileInput)
def write_file(target: str, content: str) -> str:
    """Writes content to a file by name or path within the allowed root directory."""
    try:
        allowed_dir = get_allowed_directory()
        target_path = Path(target)
        
        # 1. Resolve path
        resolved_direct = (allowed_dir / target_path).resolve() if not target_path.is_absolute() else target_path.resolve()
        
        # 2. Security Check
        if not resolved_direct.is_relative_to(allowed_dir):
            return f"Error: Access denied. '{target}' is outside allowed directory."
        
        # Ensure the parent directory exists
        resolved_direct.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content to the file
        resolved_direct.write_text(content, encoding="utf-8")
        return f"Successfully wrote to '{resolved_direct.relative_to(allowed_dir)}'."

    except Exception as e:
        return f"Error writing to file '{target}': {str(e)}"
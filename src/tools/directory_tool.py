
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from config import get_allowed_directory
class ReadDirectoryInput(BaseModel):
    target: str = Field(
        description="The directory name or relative/absolute path to list files from."
    )


@tool("read_directory", args_schema=ReadDirectoryInput)
def read_directory(target: str) -> str:
    """Searches for a directory by name or path within the allowed root directory and returns a list of files in it."""
    try:
        allowed_dir = get_allowed_directory()
        target_path = Path(target)
        
        # 1. Resolve path
        resolved_direct = (
            (allowed_dir / target_path).resolve()
            if not target_path.is_absolute()
            else target_path.resolve()
        )
        
        # 2. Direct lookup & Security Check
        if resolved_direct.exists() and resolved_direct.is_dir():
            if not resolved_direct.is_relative_to(allowed_dir):
                return f"Error: Access denied. '{target}' is outside allowed directory."
            
            items = sorted(list(resolved_direct.iterdir()))
            if not items:
                return f"Directory '{target}' is empty."
                
            item_list = [f"[DIR] {f.name}" if f.is_dir() else f"[FILE] {f.name}" for f in items]
            return "\n".join(item_list)

        # 3. Recursive Search
        search_dirname = target_path.name
        matching_dirs = [d for d in allowed_dir.rglob(search_dirname) if d.is_dir()]

        if not matching_dirs:
            return f"Error: No directory named '{target}' found anywhere in '{allowed_dir}'."

        if len(matching_dirs) > 1:
            matches_list = "\n".join([f"- {d.relative_to(allowed_dir)}" for d in matching_dirs])
            return f"Multiple directories matching '{target}' were found:\n{matches_list}\nPlease specify the exact path."

        found_dir = matching_dirs[0]
        items = sorted(list(found_dir.iterdir()))
        if not items:
            return f"Directory '{found_dir.relative_to(allowed_dir)}' is empty."
            
        item_list = [f"[DIR] {f.name}" if f.is_dir() else f"[FILE] {f.name}" for f in items]
        return "\n".join(item_list)

    except Exception as e:
        return f"Error reading directory '{target}': {str(e)}"


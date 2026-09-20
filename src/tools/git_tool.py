# src/tools/git_tools.py
import git
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from config import get_allowed_directory


def _get_repo() -> git.Repo:
    """Helper to fetch the local repository instance."""
    allowed_dir = get_allowed_directory()
    try:
        return git.Repo(allowed_dir, search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        raise ValueError(f"No git repository found at '{allowed_dir}'. Use git_init to create one.")


# 1. GIT INIT
@tool("git_init")
def git_init() -> str:
    """Initializes a new Git repository inside the configured allowed directory if one does not exist."""
    try:
        allowed_dir = get_allowed_directory()
        if (allowed_dir / ".git").exists():
            return f"Git repository already initialized at '{allowed_dir}'."
        
        repo = git.Repo.init(allowed_dir)
        return f"Initialized empty Git repository in '{allowed_dir}'."
    except Exception as e:
        return f"Error initializing repository: {str(e)}"


# 2. GIT STATUS
@tool("git_status")
def git_status() -> str:
    """Returns the working tree status (untracked, modified, staged files)."""
    try:
        repo = _get_repo()
        return repo.git.status()
    except Exception as e:
        return f"Error running git status: {str(e)}"


# 3. GIT ADD
class GitAddInput(BaseModel):
    files: str = Field(
        default=".",
        description="File path or pattern to stage (e.g., '.' for all changes, or 'src/main.py')."
    )

@tool("git_add", args_schema=GitAddInput)
def git_add(files: str = ".") -> str:
    """Stages file changes for the next commit."""
    try:
        repo = _get_repo()
        repo.git.add(files)
        return f"Successfully staged '{files}'."
    except Exception as e:
        return f"Error staging files: {str(e)}"


# 4. GIT COMMIT
class GitCommitInput(BaseModel):
    message: str = Field(description="The commit message describing the changes.")

@tool("git_commit", args_schema=GitCommitInput)
def git_commit(message: str) -> str:
    """Commits currently staged changes with the provided commit message."""
    try:
        repo = _get_repo()
        if not message.strip():
            return "Error: Commit message cannot be empty."
        result = repo.git.commit("-m", message)
        return f"Commit successful:\n{result}"
    except Exception as e:
        return f"Error committing changes: {str(e)}"


# 5. GIT DIFF
class GitDiffInput(BaseModel):
    staged: bool = Field(
        default=False,
        description="Set to True to see diff of staged changes (--staged). Default False for unstaged."
    )

@tool("git_diff", args_schema=GitDiffInput)
def git_diff(staged: bool = False) -> str:
    """Returns code diff showing unstaged or staged changes in the repository."""
    try:
        repo = _get_repo()
        diff = repo.git.diff("--staged") if staged else repo.git.diff()
        return diff if diff else "No changes found."
    except Exception as e:
        return f"Error running git diff: {str(e)}"


# 6. GIT BRANCH
class GitBranchInput(BaseModel):
    branch_name: Optional[str] = Field(
        default=None,
        description="Optional: Name of new branch to create. If empty, lists all existing branches."
    )

@tool("git_branch", args_schema=GitBranchInput)
def git_branch(branch_name: Optional[str] = None) -> str:
    """Lists local branches or creates a new branch if branch_name is provided."""
    try:
        repo = _get_repo()
        if branch_name:
            new_branch = repo.create_head(branch_name)
            return f"Created new branch '{new_branch.name}'."
        
        branches = repo.git.branch()
        return branches
    except Exception as e:
        return f"Error handling git branch: {str(e)}"


# 7. GIT CHECKOUT / SWITCH
class GitCheckoutInput(BaseModel):
    target: str = Field(description="Branch name, tag, or commit hash to checkout/switch to.")
    create_new: bool = Field(default=False, description="Set to True if creating a new branch (-b).")

@tool("git_checkout", args_schema=GitCheckoutInput)
def git_checkout(target: str, create_new: bool = False) -> str:
    """Switches branches or restores working tree files."""
    try:
        repo = _get_repo()
        if create_new:
            repo.git.checkout("-b", target)
            return f"Switched to a new branch '{target}'."
        
        repo.git.checkout(target)
        return f"Switched to branch/target '{target}'."
    except Exception as e:
        return f"Error checking out '{target}': {str(e)}"


# 8. GIT LOG
class GitLogInput(BaseModel):
    count: int = Field(default=5, description="Number of recent commits to list (default: 5).")

@tool("git_log", args_schema=GitLogInput)
def git_log(count: int = 5) -> str:
    """Returns recent commit log history."""
    try:
        repo = _get_repo()
        return repo.git.log("-n", str(count), "--oneline")
    except Exception as e:
        return f"Error fetching git log: {str(e)}"


# 9. GIT STASH
class GitStashInput(BaseModel):
    action: str = Field(
        default="push",
        description="Stash action: 'push' (save changes), 'pop' (restore and drop), or 'list'."
    )

@tool("git_stash", args_schema=GitStashInput)
def git_stash(action: str = "push") -> str:
    """Stashes modified working directory changes or lists/pops existing stashes."""
    try:
        repo = _get_repo()
        if action == "pop":
            return repo.git.stash("pop")
        elif action == "list":
            res = repo.git.stash("list")
            return res if res else "No stashed changes."
        else:
            return repo.git.stash()
    except Exception as e:
        return f"Error performing git stash: {str(e)}"


# 10. GIT PULL / PUSH
class GitRemoteInput(BaseModel):
    remote: str = Field(default="origin", description="Remote name (default: origin).")
    branch: Optional[str] = Field(default=None, description="Optional target branch.")

@tool("git_push", args_schema=GitRemoteInput)
def git_push(remote: str = "origin", branch: Optional[str] = None) -> str:
    """Pushes local commits to the remote repository."""
    try:
        repo = _get_repo()
        args = [remote]
        if branch:
            args.append(branch)
        res = repo.git.push(*args)
        return f"Successfully pushed to {remote}:\n{res or 'OK'}"
    except Exception as e:
        return f"Error pushing to remote: {str(e)}"

@tool("git_pull", args_schema=GitRemoteInput)
def git_pull(remote: str = "origin", branch: Optional[str] = None) -> str:
    """Pulls latest changes from the remote repository."""
    try:
        repo = _get_repo()
        args = [remote]
        if branch:
            args.append(branch)
        res = repo.git.pull(*args)
        return f"Successfully pulled from {remote}:\n{res or 'OK'}"
    except Exception as e:
        return f"Error pulling from remote: {str(e)}"


# Complete export list
git_tools = [
    git_init,
    git_status,
    git_add,
    git_commit,
    git_diff,
    git_branch,
    git_checkout,
    git_log,
    git_stash,
    git_push,
    git_pull,
]
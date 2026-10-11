
from langchain.agents.middleware import HumanInTheLoopMiddleware

from enum import Enum
from typing import Dict

from tools import all_tools

class ToolRisk(Enum):
    LOW = "low"            # Read-only operations (e.g., read_file, search)
    MEDIUM = "medium"      # Safe modifications (e.g., create_temp_file, format_code)
    HIGH = "high"          # File writes, commits (e.g., write_file, git_commit)
    CRITICAL = "critical"  # Shell execution, git push, DB drop

# 1. Map tool names or patterns to risk levels
RISK_REGISTRY: Dict[str, ToolRisk] = {
    # Default fallbacks by prefix
    "read_": ToolRisk.LOW,
    "list_": ToolRisk.LOW,
    "search_": ToolRisk.LOW,
    "write_": ToolRisk.HIGH,
    "edit_": ToolRisk.HIGH,
    "git_": ToolRisk.HIGH,
    "execute_": ToolRisk.CRITICAL,
    "terminal_": ToolRisk.CRITICAL,
}

# 2. Set environment-based policy threshold (e.g., interrupt on HIGH and CRITICAL)
REQUIRED_APPROVAL_LEVELS = {ToolRisk.HIGH, ToolRisk.CRITICAL}

def evaluate_tool_risk(tool_name: str) -> bool:
    # Check exact match first, then prefix match
    if tool_name in RISK_REGISTRY:
        return RISK_REGISTRY[tool_name] in REQUIRED_APPROVAL_LEVELS
    
    for prefix, risk in RISK_REGISTRY.items():
        if tool_name.startswith(prefix):
            return risk in REQUIRED_APPROVAL_LEVELS
            
    # Default safe fallback: interrupt unknown tools by default
    return True

# 3. Generate interrupt dictionary dynamically
def build_risk_based_hitl(all_tools):
    return {tool.name: evaluate_tool_risk(tool.name) for tool in all_tools}

middlewares=[
        HumanInTheLoopMiddleware(
            interrupt_on=build_risk_based_hitl(all_tools),
            description_prefix="Tool execution requires approval",
        ),
    ]
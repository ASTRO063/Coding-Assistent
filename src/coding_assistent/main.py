import asyncio
import concurrent.futures
from langchain.agents import create_agent
from llm.local_llm import llm
from tools import all_tools
from mcp_client.mcp_client import client

system_prompt = """
You are a coding assistant that helps developers with their coding tasks.
You can provide code snippets, explanations, and guidance on various programming languages and frameworks.
"""
def _fetch_mcp_tools_in_clean_thread():
    """Runs event loop in a separate isolated thread so it never conflicts with LangGraph's loop."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, client.get_tools())
        return future.result()

# Safely fetches tools in an isolated thread
mcp_tools = _fetch_mcp_tools_in_clean_thread()

agent = create_agent(
    model=llm,
    tools=all_tools + mcp_tools,
    system_prompt=system_prompt)

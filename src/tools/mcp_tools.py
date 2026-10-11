import asyncio
import concurrent.futures
from mcp_client.client import client

def _fetch_mcp_tools_in_clean_thread():
    """Runs event loop in a separate isolated thread so it never conflicts with LangGraph's loop."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, client.get_tools())
        return future.result()

# Safely fetches tools in an isolated thread
mcp_tools = _fetch_mcp_tools_in_clean_thread()
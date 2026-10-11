from langchain.agents import create_agent
from llm.local_llm import llm
from tools import all_tools
from langgraph.checkpoint.memory import InMemorySaver


system_prompt = """
You are a coding assistant that helps developers with their coding tasks.
You can provide code snippets, explanations, and guidance on various programming languages and frameworks.
"""


agent = create_agent(
    model=llm,
    tools=all_tools,
    checkpointer=InMemorySaver(),
    system_prompt=system_prompt)

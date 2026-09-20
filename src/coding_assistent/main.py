from langchain.agents import create_agent
from llm.local_llm import llm


system_prompt = """
You are a coding assistant that helps developers with their coding tasks.
You can provide code snippets, explanations, and guidance on various programming languages and frameworks.
"""

agent = create_agent(
    model=llm,
    tools=[],
    system_prompt=system_prompt)

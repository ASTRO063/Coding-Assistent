import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()
from typing import Generator
from langchain_core.messages import HumanMessage, AIMessage
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from coding_assistent import agent
from rich.live import Live

# Initialize Rich Console
console = Console()

async def run_terminal_agent(agent_executor):
    """
    Async terminal loop for LangChain agents using astream_events v2.
    Provides live token streaming and clear visibility into tool executions.
    """
    console.clear()
    console.print(
        Panel.fit(
            "[bold green]Coding Assistant CLI[/bold green]\n"
            "Type [bold cyan]'exit'[/bold cyan] or [bold cyan]'quit'[/bold cyan] to stop.\n"
            "Type [bold cyan]'clear'[/bold cyan] to reset conversation history.",
            title="Welcome",
            border_style="green"
        )
    )

    # Note: chat_history and config are not fully utilized in the current provided code, 
    # but we keep them for structural integrity.
    chat_history = []
    config = {"configurable": {"thread_id": "1"}}

    while True:
        try:
            # Capture user input using Rich Prompt
            user_input = Prompt.ask("\n[bold blue]User[/bold blue]").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                console.print("[bold yellow]Exiting Coding Assistant. Goodbye![/bold yellow]")
                break

            if user_input.lower() == "clear":
                chat_history.clear()
                console.clear()
                console.print("[bold green]Chat history cleared.[/bold green]")
                continue

            # Start the assistant response prefix
            console.print("\n[bold magenta]Assistant[/bold magenta]: ", end="")

            full_response = ""
            in_tool_call = False

            # Stream events using v2 engine (REMOVED REDUNDANT AGENT.STREAM CALL)
            async for event in agent.astream_events(
                {"messages": [HumanMessage(user_input)]},
                config = config,
                version="v2"
            ):
                event_type = event["event"]

                # 1. Catch streaming LLM tokens
                if event_type == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if hasattr(chunk, "content") and chunk.content:
                        content = chunk.content
                        if isinstance(content, str):
                            # If coming back from a tool call, print assistant prompt prefix
                            if in_tool_call:
                                console.print("\n[bold magenta]Assistant[/bold magenta]: ", end="")
                                in_tool_call = False
                            
                            sys.stdout.write(content)
                            sys.stdout.flush()
                            full_response += content

                # 2. Catch tool start events
                elif event_type == "on_tool_start":
                    in_tool_call = True
                    tool_name = event.get("name", "Tool")
                    tool_input = event["data"].get("input", {})
                    
                    console.print(
                        f"\n[bold yellow]⚙ Executing Tool {tool_name}...[/bold yellow]"
                    )
                    if tool_input:
                        console.print(f"[dim]Args: {tool_input}[/dim]")

                # 3. Catch tool end events
                elif event_type == "on_tool_end":
                    tool_name = event.get("name", "Tool")
                    console.print(f"[bold green]✔ Tool {tool_name} finished.[/bold green]")

            # Ensure a new line is printed after the response completes
            console.print()

            # Record chat history
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=full_response))

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Session interrupted. Type 'exit' to quit.[/bold yellow]")
        except Exception as e:
            console.print(f"\n[bold red]Error during execution:[/bold red] {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_terminal_agent(agent))
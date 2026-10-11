import asyncio
from dotenv import load_dotenv

load_dotenv()

from invoke.agent_stream import stream_agent_execution
from langchain_core.messages import HumanMessage
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from coding_assistent import agent

# Initialize Rich Console
console = Console()

async def run_terminal_agent(agent_executor):
    """
    Async terminal loop for LangChain/LangGraph agents.
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

    config = {"configurable": {"thread_id": "1"}}

    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]User[/bold blue]").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                console.print("[bold yellow]Exiting Coding Assistant. Goodbye![/bold yellow]")
                break

            if user_input.lower() == "clear":
                console.clear()
                console.print("[bold green]Chat history cleared.[/bold green]")
                continue

            console.print("\n[bold magenta]Assistant[/bold magenta]: ", end="")

            # Initiate graph stream with human message
            llm_input = {"messages": [HumanMessage(content=user_input)]}
            await stream_agent_execution(llm_input, config, agent)

            console.print()

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Session interrupted. Type 'exit' to quit.[/bold yellow]")
        except Exception as e:
            console.print(f"\n[bold red]Error during execution:[/bold red] {str(e)}")


if __name__ == "__main__":
    asyncio.run(run_terminal_agent(agent))
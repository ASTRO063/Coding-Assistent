import sys
from dotenv import load_dotenv

load_dotenv()
from typing import Generator
from langchain_core.messages import HumanMessage, AIMessage
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.live import Live
from rich.markdown import Markdown
from coding_assistent import agent

from dotenv import load_dotenv

# load_dotenv("")
# PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# Initialize Rich Console
console = Console()

def terminal_agent(agent_executor):
    """
    Runs an interactive CLI loop for the LangChain agent.
    """
    console.clear()
    console.print(
        Panel.fit(
            "[bold green]Coding Assistant CLI[/bold green]\n"
            "Type [bold cyan]'exit'[/bold cyan] or [bold cyan]'quit'[/bold cyan] to stop.\n"
            "Type [bold cyan]'clear'[/bold cyan] to reset chat memory.",
            title="Welcome",
            border_style="green"
        )
    )

    # Maintain session conversation history
    chat_history = []

    while True:
        try:
            # Capture user prompt
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

            console.print("\n[bold magenta]Assistant[/bold magenta]:", end=" ")

            full_response = ""
            print(f"user_input", user_input)
            # Stream response or invoke agent
            question = HumanMessage(content=user_input)
            response_text = agent_executor.invoke({"messages": [question]})
            print(response_text['messages'][1].content)
            
            # Using stream (if your agent executor / LangGraph supports streaming)
            with Live(console=console, refresh_per_second=15, vertical_overflow="visible") as live:
                for token, metadata in agent.stream(
                    {
                        "input": user_input,
                        "chat_history": chat_history,
                    },
                    stream_mode="messages"
                ):
                    # Check token for text content
                    if hasattr(token, "content") and token.content:
                        print("token --", token)
                        if isinstance(token.content, str):
                            full_response += token.content
                        elif isinstance(token.content, list):
                            for block in token.content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    full_response += block.get("text", "")
                        
                        live.update(Markdown(full_response))

            # Record history
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=full_response))

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Session interrupted. Type 'exit' to quit.[/bold yellow]")
        except Exception as e:
            console.print(f"\n[bold red]Error during execution:[/bold red] {str(e)}")

        # except KeyboardInterrupt:
        #     console.print("\n[bold yellow]Session interrupted. Type 'exit' to quit.[/bold yellow]")
        # except Exception as e:
        #     console.print(f"\n[bold red]Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    # Replace `your_agent_executor` with your existing agent instance
    terminal_agent(agent)
    pass
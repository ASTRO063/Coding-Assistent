import sys
from typing import Any, Dict
from langgraph.types import Command
from coding_assistent.main import agent

from rich.console import Console
from rich.table import Table
import questionary
from questionary import Choice
from rich.syntax import Syntax
from rich.panel import Panel

console = Console()

async def stream_agent_execution(input_data: Any, config: dict, agent):
    """
    Streams agent events and recursively handles interrupts when triggered.
    """
    in_tool_call = False
    full_response = ""

    async for event in agent.astream_events(
        input_data,
        config=config,
        version="v2"
    ):
        event_type = event["event"]

        # 1. Catch interruption  
        if event_type == "on_chain_stream":
            chunk = event["data"]["chunk"]

            # Intercept Human-in-the-Loop interrupt signal
            if isinstance(chunk, dict) and "__interrupt__" in chunk:
                interrupts = chunk["__interrupt__"]
                for interrupt in interrupts:
                    interrupt_val = interrupt.value
                    
                    # 1. Await UI & get decision Command asynchronously
                    resume_command = await render_and_prompt_approval(interrupt_val)
                    
                    # 2. Resume execution recursively with the decision command
                    await stream_agent_execution(resume_command, config, agent)
                    return

        # 2. Catch streaming LLM tokens
        elif event_type == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if hasattr(chunk, "content") and chunk.content:
                content = chunk.content
                if isinstance(content, str):
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

            console.print(f"\n[bold yellow]⚙ Executing Tool {tool_name}...[/bold yellow]")
            if tool_input:
                console.print(f"[dim]Args: {tool_input}[/dim]")

        # 3. Catch tool end events
        elif event_type == "on_tool_end":
            tool_name = event.get("name", "Tool")
            console.print(f"[bold green]✔ Tool {tool_name} finished.[/bold green]")

async def render_and_prompt_approval(interrupt_val: Dict[str, Any]) -> Command:
    """
    Async renderer and prompt handler for human-in-the-loop approvals.
    Sends properly structured decision payloads back to middleware.
    """
    action_requests = interrupt_val.get("action_requests", [])
    if not action_requests:
        console.print("[bold red]No action requests found in interrupt payload.[/bold red]")
        return Command(resume={"decisions": [{"type": "reject"}]})

    req = action_requests[0]
    tool_name = req.get("name", "Unknown Tool")
    args = req.get("args", {})

    console.print("\n[bold yellow]⚠️  HUMAN APPROVAL REQUIRED[/bold yellow]\n")

    # Render target file and code preview if writing a file
    if tool_name in ["write_file"] and "content" in args:
        target_file = args.get("target", "file")
        content = args.get("content", "")

        console.print(f"[bold cyan]Tool:[bold cyan] [green]{tool_name}[/green]")
        console.print(f"[bold cyan]Target:[bold cyan] [yellow]{target_file}[/yellow]\n")

        lexer = "python"

        syntax = Syntax(content, lexer, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"Proposed changes to [bold]{target_file}[/bold]", border_style="cyan"))
    else:
        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Argument", style="cyan", width=20)
        table.add_column("Value", style="white")

        for k, v in args.items():
            table.add_row(str(k), str(v))

        console.print(Panel(table, title=f"Tool Execution: [bold green]{tool_name}[/bold green]", border_style="yellow"))

    return await decision(args, tool_name)

async def decision(args: Any, tool_name: Any):
    choices = [
        Choice("Approve execution", value="approve"),
        Choice("Edit content / arguments", value="edit"),
        Choice("Provide feedback / instructions", value="respond"),
        Choice("Reject execution", value="reject"),
    ]
        
    selected_action = await questionary.select(
            "Select an action using arrow keys:",
            choices=choices,
            style=questionary.Style([
                ('qmark', 'fg:#e5c07b bold'),
                ('question', 'bold white'),
                ('pointer', 'fg:#61afef bold'),
                ('highlighted', 'fg:#61afef bold'),
                ('selected', 'fg:#98c379 bold'),
            ])
        ).ask_async()
    
    if selected_action == "approve":
        console.print("[bold green]✔ Action Approved.[/bold green]\n")
        return Command(resume={"decisions": [{"type": "approve"}]})

    elif selected_action == "reject":
        console.print("[bold red]✘ Action Rejected.[/bold red]\n")
        return Command(resume={"decisions": [{"type": "reject"}]})

    elif selected_action == "edit":
        if "content" in args:
            edited_content = await questionary.text(
                "Enter updated content:",
                default=str(args.get("content", ""))
            ).ask_async()
            updated_args = {**args, "content": edited_content}
        else:
            edited_args_str = await questionary.text(
                "Enter updated args dictionary/text:",
                default=str(args)
            ).ask_async()
            updated_args = edited_args_str

        # Updated payload format expected by the middleware for edit actions
        edited_action = {
            "name": tool_name,
            "args": updated_args
        }

        return Command(resume={
            "decisions": [
                {
                    "type": "edit",
                    "edited_action": edited_action,
                    "action": edited_action
                }
            ]
        })

    elif selected_action == "respond":
            feedback = await questionary.text("Enter instructions for the agent:").ask_async()
            return Command(resume={"decisions": [{"type": "respond", "message": feedback}]})

    return Command(resume={"decisions": [{"type": "reject"}]})
    
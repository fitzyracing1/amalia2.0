"""
Amalia 2.0 CLI (stub using Typer)
"""

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    name="amalia2",
    help="Amalia 2.0 — Modern tooling for Portugal's National LLM",
    add_completion=False,
)
console = Console()


@app.command()
def version():
    """Show version"""
    from amalia2 import __version__
    console.print(f"[bold green]amalia2[/] v{__version__}")


@app.command()
def chat(
    model: str = typer.Option("amalia-9b", "--model", "-m"),
    system: str = typer.Option("", "--system", "-s"),
):
    """Start an interactive chat session with Amália"""
    console.print(Panel.fit(
        f"[bold]Starting chat with[/] [green]{model}[/]\n"
        "This is a placeholder. Full interactive chat coming in next iteration.",
        title="Amalia 2.0 Chat",
        border_style="green"
    ))


@app.command()
def new(
    project_name: str = typer.Argument(..., help="Name of the new project"),
    template: str = typer.Option("basic", "--template", "-t", help="Template to use"),
):
    """Scaffold a new project from template"""
    console.print(f"[green]Creating new project[/] [bold]{project_name}[/] using template [cyan]{template}[/]")
    console.print("Scaffolding logic will be implemented in the next version.")


def main():
    app()


if __name__ == "__main__":
    main()
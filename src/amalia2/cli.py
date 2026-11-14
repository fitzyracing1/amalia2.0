"""Amalia 2.0 CLI (Typer + Rich)."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import typer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from amalia2.client import AmaliaClient
from amalia2.config import AmaliaConfig, load_config
from amalia2.errors import AmaliaError

app = typer.Typer(
    name="amalia2",
    help="Amalia 2.0 — Modern tooling for Portugal's National LLM",
    add_completion=False,
)
console = Console()


def _streaming_panel(text: str) -> Panel:
    body = Text(text or "…", style="dim")
    return Panel(body, title="Amália (streaming)", border_style="grey50")


class ChatSession:
    """Interactive Rich chat loop over an IAEdu agent stream."""

    def __init__(
        self,
        client: AmaliaClient,
        *,
        thread_id: str | None = None,
        system: str = "",
        rich_console: Console | None = None,
    ) -> None:
        self.client = client
        self.thread_id = thread_id or client.new_thread_id()
        self.system = system
        self._system_sent = False
        self.turns = 0
        self.console = rich_console if rich_console is not None else console

    async def send(self, prompt: str) -> str | None:
        message = prompt
        if self.system and not self._system_sent:
            message = f"{self.system.rstrip()}\n\n{prompt}"
            self._system_sent = True

        chunks: list[str] = []
        final_text: str | None = None
        try:
            with Live(
                _streaming_panel(""),
                console=self.console,
                refresh_per_second=16,
                transient=True,
            ) as live:
                async for ev in self.client.stream(message, thread_id=self.thread_id):
                    if ev.type == "token" and isinstance(ev.content, str):
                        chunks.append(ev.content)
                        live.update(_streaming_panel("".join(chunks)))
                    elif ev.type == "message" and isinstance(ev.content, dict):
                        text = ev.content.get("content")
                        if isinstance(text, str) and text:
                            final_text = text
        except AmaliaError as e:
            self.console.print(f"[red]error:[/red] {e}")
            return None

        reply = final_text if final_text is not None else "".join(chunks)
        body: Markdown | Text = Markdown(reply) if reply else Text("…", style="dim")
        self.console.print(Panel(body, title="Amália", border_style="cyan"))
        self.turns += 1
        return reply

    def cmd_new(self, _arg: str) -> None:
        self.thread_id = self.client.new_thread_id()
        self.turns = 0
        self._system_sent = False
        self.console.print(f"[dim]New thread: {self.thread_id}[/dim]")

    def cmd_thread(self, arg: str) -> None:
        if arg:
            self.thread_id = arg
            self.turns = 0
            self._system_sent = False
            self.console.print(
                f"[dim]Switched to thread {self.thread_id} (history reset locally)[/dim]"
            )
        else:
            self.console.print(f"[dim]thread_id: {self.thread_id} · turns: {self.turns}[/dim]")

    def cmd_help(self, _arg: str) -> None:
        self.console.print(
            "[dim]Commands:\n"
            "  /new            start a fresh thread\n"
            "  /thread [id]    show or switch thread id\n"
            "  /help           show this help\n"
            "  /exit           quit (or Ctrl-D)\n"
            "[/dim]"
        )


_COMMANDS: dict[str, Callable[[ChatSession, str], None]] = {
    "/new": ChatSession.cmd_new,
    "/thread": ChatSession.cmd_thread,
    "/help": ChatSession.cmd_help,
}


async def run_chat_session(
    session: ChatSession,
    *,
    read_line: Callable[[], str] | None = None,
) -> int:
    session.console.print(
        Panel.fit(
            "[bold]Amália 2.0[/bold] — interactive chat\n"
            "Type a message and press Enter. [dim]/help[/dim] for commands, "
            "[dim]Ctrl-D[/dim] to exit.",
            title="Amalia 2.0 Chat",
            border_style="green",
        )
    )
    session.console.print(f"[dim]thread: {session.thread_id}[/dim]\n")

    get_line = read_line or (lambda: session.console.input("[bold cyan]you ›[/] "))

    while True:
        try:
            line = get_line()
        except EOFError:
            session.console.print("\n[dim]bye.[/dim]")
            return 0
        except KeyboardInterrupt:
            session.console.print("\n[dim]bye.[/dim]")
            return 0

        text = line.strip()
        if not text:
            continue
        if text in {"/exit", "/quit"}:
            return 0
        if text.startswith("/"):
            head, _, rest = text.partition(" ")
            handler = _COMMANDS.get(head)
            if handler is None:
                session.console.print(f"[yellow]unknown command: {head} (try /help)[/yellow]")
            else:
                handler(session, rest.strip())
            continue
        await session.send(text)


async def _interactive_chat(
    config: AmaliaConfig,
    *,
    system: str,
    thread_id: str | None,
) -> int:
    async with AmaliaClient(config) as client:
        session = ChatSession(client, thread_id=thread_id, system=system)
        return await run_chat_session(session)


@app.command()
def version() -> None:
    """Show version"""
    from amalia2 import __version__

    console.print(f"[bold green]amalia2[/] v{__version__}")


@app.command()
def chat(
    system: str = typer.Option("", "--system", "-s", help="Prefix included with the first message"),
    thread: str | None = typer.Option(
        None, "--thread", help="Reuse a thread id for server-side memory"
    ),
) -> None:
    """Start an interactive chat session with Amália."""
    try:
        config = load_config()
    except AmaliaError as e:
        console.print(f"[red]error:[/red] {e}")
        raise typer.Exit(code=1) from e

    try:
        code = asyncio.run(_interactive_chat(config, system=system, thread_id=thread))
    except KeyboardInterrupt:
        console.print("\n[dim]bye.[/dim]")
        raise typer.Exit(code=0) from None
    raise typer.Exit(code=code)


@app.command()
def new(
    project_name: str = typer.Argument(..., help="Name of the new project"),
    template: str = typer.Option("basic", "--template", "-t", help="Template to use"),
) -> None:
    """Scaffold a new project from template (not yet implemented)."""
    console.print(
        f"[green]Creating new project[/] [bold]{project_name}[/] "
        f"using template [cyan]{template}[/]"
    )
    console.print(
        "Scaffolding is a follow-up (phase 03). "
        "`amalia2 new` is still a stub and does not write files."
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()

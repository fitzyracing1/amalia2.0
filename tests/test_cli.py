"""Tests for the amalia2 Typer CLI using CliRunner."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from amalia2 import __version__
from amalia2.cli import ChatSession, app, run_chat_session
from amalia2.client import StreamEvent
from amalia2.config import AmaliaConfig
from amalia2.errors import AmaliaAuthError

runner = CliRunner()

SAMPLE = AmaliaConfig(api_key="k", agent_id="ag", channel_id="ch")


class FakeClient:
    def __init__(
        self,
        events: list[StreamEvent] | None = None,
        *,
        error: Exception | None = None,
    ) -> None:
        self.events = events or [
            StreamEvent(type="token", content="Olá ", raw={"type": "token", "content": "Olá "}),
            StreamEvent(type="token", content="mundo", raw={"type": "token", "content": "mundo"}),
            StreamEvent(
                type="message",
                content={"content": "Olá mundo"},
                raw={"type": "message", "content": {"content": "Olá mundo"}},
            ),
        ]
        self.error = error
        self.prompts: list[tuple[str, str]] = []
        self._thread_n = 0

    def new_thread_id(self) -> str:
        self._thread_n += 1
        return f"thread-{self._thread_n}"

    async def stream(
        self,
        message: str,
        *,
        thread_id: str,
        **kwargs: Any,
    ) -> AsyncIterator[StreamEvent]:
        self.prompts.append((message, thread_id))
        if self.error is not None:
            raise self.error
        for ev in self.events:
            yield ev


def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "AMALIA_API_KEY",
        "AMALIA_AGENT_ID",
        "AMALIA_CHANNEL_ID",
        "AMALIA_BASE_URL",
    ):
        monkeypatch.delenv(key, raising=False)


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_chat_fails_clearly_without_credentials(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _clear_env(monkeypatch)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("amalia2.config.Path.home", lambda: tmp_path)
    result = runner.invoke(app, ["chat"])
    assert result.exit_code == 1
    assert "Missing required Amália config" in result.output
    assert "AMALIA_API_KEY" in result.output
    assert "placeholder" not in result.output.lower()


def test_new_prints_stub_message() -> None:
    result = runner.invoke(app, ["new", "my-app", "--template", "rag-chatbot"])
    assert result.exit_code == 0
    assert "my-app" in result.output
    assert "rag-chatbot" in result.output
    assert "stub" in result.output.lower() or "follow-up" in result.output.lower()


def test_new_requires_project_name() -> None:
    result = runner.invoke(app, ["new"])
    assert result.exit_code != 0


async def test_chat_session_streams_tokens() -> None:
    client = FakeClient()
    session = ChatSession(client, thread_id="t-1")
    reply = await session.send("Olá")
    assert reply == "Olá mundo"
    assert client.prompts == [("Olá", "t-1")]
    assert session.turns == 1


async def test_chat_session_prepends_system_once() -> None:
    client = FakeClient()
    session = ChatSession(client, system="Fala em pt-PT.")
    await session.send("Olá")
    await session.send("Outra")
    assert client.prompts[0][0].startswith("Fala em pt-PT.")
    assert client.prompts[0][0].endswith("Olá")
    assert client.prompts[1][0] == "Outra"


async def test_chat_session_reports_auth_error() -> None:
    client = FakeClient(error=AmaliaAuthError("Authentication failed (HTTP 401)."))
    session = ChatSession(client)
    reply = await session.send("Olá")
    assert reply is None
    assert session.turns == 0


async def test_repl_exit_and_help() -> None:
    client = FakeClient()
    session = ChatSession(client)
    lines = iter(["/help", "/exit"])
    code = await run_chat_session(session, read_line=lambda: next(lines))
    assert code == 0
    assert client.prompts == []


def test_chat_command_runs_session(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setenv("AMALIA_API_KEY", "k")
    monkeypatch.setenv("AMALIA_AGENT_ID", "ag")
    monkeypatch.setenv("AMALIA_CHANNEL_ID", "ch")

    class FakeAmaliaClient:
        def __init__(self, config: AmaliaConfig, **kwargs: Any) -> None:
            self._inner = FakeClient()

        async def __aenter__(self) -> FakeClient:
            return self._inner

        async def __aexit__(self, *args: object) -> None:
            return None

    monkeypatch.setattr("amalia2.cli.AmaliaClient", FakeAmaliaClient)
    result = runner.invoke(app, ["chat"], input="Olá\n/exit\n")
    assert result.exit_code == 0
    assert "Amalia 2.0 Chat" in result.output
    assert "Olá mundo" in result.output
    assert "placeholder" not in result.output.lower()

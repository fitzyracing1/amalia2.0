"""Tests for the amalia2 Typer CLI using CliRunner."""

from __future__ import annotations

from typer.testing import CliRunner

from amalia2 import __version__
from amalia2.cli import app

runner = CliRunner()


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_chat_is_a_placeholder() -> None:
    result = runner.invoke(app, ["chat", "--model", "amalia-9b-instruct"])
    assert result.exit_code == 0
    assert "amalia-9b-instruct" in result.output
    assert "placeholder" in result.output


def test_new_prints_stub_message() -> None:
    result = runner.invoke(app, ["new", "my-app", "--template", "rag-chatbot"])
    assert result.exit_code == 0
    assert "my-app" in result.output
    assert "rag-chatbot" in result.output


def test_new_requires_project_name() -> None:
    result = runner.invoke(app, ["new"])
    assert result.exit_code != 0

"""Tests for env / creds.txt config loading (no live secrets)."""

from __future__ import annotations

from pathlib import Path

import pytest

from amalia2 import AmaliaClient, AmaliaError, load_config
from amalia2.config import DEFAULT_BASE_URL, AmaliaConfig

CREDS = """\
Endpoint: https://api.iaedu.pt/agent-chat//api/v1/agent/file-agent/stream
API Key: sk-usr-file
ChannelID: file-channel
"""


def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "AMALIA_API_KEY",
        "AMALIA_AGENT_ID",
        "AMALIA_CHANNEL_ID",
        "AMALIA_BASE_URL",
    ):
        monkeypatch.delenv(key, raising=False)


def test_load_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setenv("AMALIA_API_KEY", "sk-env")
    monkeypatch.setenv("AMALIA_AGENT_ID", "env-agent")
    monkeypatch.setenv("AMALIA_CHANNEL_ID", "env-channel")
    config = load_config()
    assert config == AmaliaConfig(
        api_key="sk-env",
        agent_id="env-agent",
        channel_id="env-channel",
        base_url=DEFAULT_BASE_URL,
    )


def test_load_config_optional_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setenv("AMALIA_API_KEY", "sk-env")
    monkeypatch.setenv("AMALIA_AGENT_ID", "env-agent")
    monkeypatch.setenv("AMALIA_CHANNEL_ID", "env-channel")
    monkeypatch.setenv("AMALIA_BASE_URL", "https://example.test/agent-chat")
    config = load_config()
    assert config.base_url == "https://example.test/agent-chat"
    assert config.stream_url().startswith("https://example.test/agent-chat//api/v1/agent/")


def test_missing_config_raises_typed_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _clear_env(monkeypatch)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("amalia2.config.Path.home", lambda: tmp_path)
    with pytest.raises(AmaliaError, match="AMALIA_API_KEY") as excinfo:
        load_config()
    msg = str(excinfo.value)
    assert "AMALIA_AGENT_ID" in msg
    assert "AMALIA_CHANNEL_ID" in msg
    assert "creds.txt" in msg


def test_client_init_without_config_uses_load_config(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _clear_env(monkeypatch)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("amalia2.config.Path.home", lambda: tmp_path)
    with pytest.raises(AmaliaError, match="Missing required Amália config"):
        AmaliaClient()


def test_creds_file_fallback(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _clear_env(monkeypatch)
    creds = tmp_path / "creds.txt"
    creds.write_text(CREDS, encoding="utf-8")
    config = load_config(creds)
    assert config.api_key == "sk-usr-file"
    assert config.agent_id == "file-agent"
    assert config.channel_id == "file-channel"
    assert config.base_url == "https://api.iaedu.pt/agent-chat"


def test_cwd_creds_txt(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _clear_env(monkeypatch)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("amalia2.config.Path.home", lambda: tmp_path)
    (tmp_path / "creds.txt").write_text(CREDS, encoding="utf-8")
    config = load_config()
    assert config.agent_id == "file-agent"
    assert config.api_key == "sk-usr-file"


def test_home_creds_txt(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _clear_env(monkeypatch)
    monkeypatch.chdir(tmp_path)
    home = tmp_path / "home"
    (home / ".amalia").mkdir(parents=True)
    (home / ".amalia" / "creds.txt").write_text(CREDS, encoding="utf-8")
    monkeypatch.setattr("amalia2.config.Path.home", lambda: home)
    config = load_config()
    assert config.channel_id == "file-channel"


def test_env_overrides_creds_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setenv("AMALIA_API_KEY", "sk-env")
    creds = tmp_path / "creds.txt"
    creds.write_text(CREDS, encoding="utf-8")
    config = load_config(creds)
    assert config.api_key == "sk-env"
    assert config.agent_id == "file-agent"
    assert config.channel_id == "file-channel"

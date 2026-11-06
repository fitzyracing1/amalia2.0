"""Load Amália IAEdu credentials from the environment or a creds.txt file."""

from __future__ import annotations

import os
import re
from pathlib import Path

from pydantic import BaseModel, Field

from .errors import AmaliaError

DEFAULT_BASE_URL = "https://api.iaedu.pt/agent-chat"
DEFAULT_TIMEOUT = 120.0

_AGENT_ID_RE = re.compile(r"/agent/([A-Za-z0-9_-]+)")
_API_KEY_RE = re.compile(r"API\s*Key\s*:\s*(\S+)", re.IGNORECASE)
_CHANNEL_RE = re.compile(r"Channel\s*ID\s*:\s*(\S+)", re.IGNORECASE)
_ENDPOINT_RE = re.compile(r"Endpoint\s*:\s*(\S+)", re.IGNORECASE)


class AmaliaConfig(BaseModel):
    """Connection settings for the IAEdu agent-chat API."""

    api_key: str
    agent_id: str
    channel_id: str
    base_url: str = DEFAULT_BASE_URL
    timeout: float = Field(default=DEFAULT_TIMEOUT, gt=0)

    def stream_url(self) -> str:
        """Return the NDJSON stream endpoint.

        The double slash after the base path matches the official example
        Endpoint shipped with IAEdu accounts.
        """
        base = self.base_url.rstrip("/")
        return f"{base}//api/v1/agent/{self.agent_id}/stream"


def _candidate_creds_paths(explicit: Path | None) -> list[Path]:
    if explicit is not None:
        return [explicit]
    return [
        Path.cwd() / "creds.txt",
        Path.home() / ".amalia" / "creds.txt",
    ]


def _parse_creds_file(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    if m := _API_KEY_RE.search(text):
        out["api_key"] = m.group(1)
    if m := _CHANNEL_RE.search(text):
        out["channel_id"] = m.group(1)
    if m := _ENDPOINT_RE.search(text):
        endpoint = m.group(1)
        if am := _AGENT_ID_RE.search(endpoint):
            out["agent_id"] = am.group(1)
        if "/api/v1" in endpoint:
            out["base_url"] = endpoint.split("/api/v1", 1)[0].rstrip("/")
    return out


def load_config(creds_path: Path | None = None) -> AmaliaConfig:
    """Resolve config from env vars, falling back to a creds.txt file.

    Lookup order: ``AMALIA_*`` env vars first, then ``./creds.txt``, then
    ``~/.amalia/creds.txt`` (or the explicit path passed in). Raises
    :class:`AmaliaError` listing what's missing.
    """
    values: dict[str, str] = {}
    for key, env in (
        ("api_key", "AMALIA_API_KEY"),
        ("agent_id", "AMALIA_AGENT_ID"),
        ("channel_id", "AMALIA_CHANNEL_ID"),
        ("base_url", "AMALIA_BASE_URL"),
    ):
        if v := os.environ.get(env):
            values[key] = v

    needed = {"api_key", "agent_id", "channel_id"}
    if not needed.issubset(values):
        for path in _candidate_creds_paths(creds_path):
            if path.is_file():
                for k, v in _parse_creds_file(path).items():
                    values.setdefault(k, v)
                break

    missing = [k for k in needed if k not in values]
    if missing:
        env_names = {
            "api_key": "AMALIA_API_KEY",
            "agent_id": "AMALIA_AGENT_ID",
            "channel_id": "AMALIA_CHANNEL_ID",
        }
        hints = ", ".join(f"{k} (set ${env_names[k]})" for k in missing)
        raise AmaliaError(
            f"Missing required Amália config: {hints}. "
            "Alternatively, place a creds.txt in the current directory or ~/.amalia/."
        )

    return AmaliaConfig(
        api_key=values["api_key"],
        agent_id=values["agent_id"],
        channel_id=values["channel_id"],
        base_url=values.get("base_url", DEFAULT_BASE_URL),
    )

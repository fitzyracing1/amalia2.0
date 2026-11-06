"""Async IAEdu agent-chat client for Amália."""

from __future__ import annotations

import json
import secrets
from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import TracebackType
from typing import IO, Any

import httpx
from typing_extensions import Self

from .config import AmaliaConfig, load_config
from .errors import AmaliaAuthError, AmaliaError, AmaliaHTTPError

USER_AGENT = "amalia2/0.1.0-alpha"


@dataclass(frozen=True)
class StreamEvent:
    """One NDJSON event from the IAEdu agent stream."""

    type: str  # "start" | "token" | "message" | "done" | (anything new)
    content: Any
    run_id: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


class AmaliaClient:
    """Async client for the IAEdu Amália agent-chat streaming API."""

    def __init__(
        self,
        config: AmaliaConfig | None = None,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        timeout: float | None = None,
    ) -> None:
        self.config = config if config is not None else load_config()
        timeout_s = timeout if timeout is not None else self.config.timeout
        self._client = httpx.AsyncClient(
            timeout=timeout_s,
            headers={
                "User-Agent": USER_AGENT,
                "x-api-key": self.config.api_key,
            },
            transport=transport,
        )

    @staticmethod
    def new_thread_id() -> str:
        """Return a short URL-safe id for a new conversation thread."""
        return secrets.token_urlsafe(15)

    async def stream(
        self,
        message: str,
        *,
        thread_id: str,
        user_info: Mapping[str, Any] | str | None = None,
        user_id: str | None = None,
        user_context: Mapping[str, Any] | str | None = None,
        image: str | Path | IO[bytes] | None = None,
    ) -> AsyncIterator[StreamEvent]:
        """POST a message and yield :class:`StreamEvent` values as they arrive."""
        files: list[tuple[str, Any]] = [
            ("channel_id", (None, self.config.channel_id)),
            ("thread_id", (None, thread_id)),
            ("user_info", (None, _as_json_field(user_info if user_info is not None else {}))),
            ("message", (None, message)),
        ]
        if user_id is not None:
            files.append(("user_id", (None, user_id)))
        if user_context is not None:
            files.append(("user_context", (None, _as_json_field(user_context))))

        image_handle: IO[bytes] | None = None
        try:
            if image is not None:
                image_handle, image_tuple = _open_image(image)
                files.append(("image", image_tuple))

            try:
                async with self._client.stream(
                    "POST",
                    self.config.stream_url(),
                    files=files,
                ) as response:
                    async for event in _iter_stream_events(response):
                        yield event
            except httpx.RequestError as e:
                raise AmaliaError(f"Network error talking to Amália: {e}") from e
        finally:
            if image_handle is not None:
                image_handle.close()

    async def complete(self, message: str, **kwargs: Any) -> str:
        """Stream a turn and return the final reply as a single string.

        Prefers the canonical text from the ``message`` event; falls back to
        concatenated ``token`` chunks if the server does not send one.
        """
        tokens: list[str] = []
        final: str | None = None
        async for ev in self.stream(message, **kwargs):
            if ev.type == "token" and isinstance(ev.content, str):
                tokens.append(ev.content)
            elif ev.type == "message" and isinstance(ev.content, dict):
                text = ev.content.get("content")
                if isinstance(text, str) and text:
                    final = text
        return final if final is not None else "".join(tokens)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()


async def _iter_stream_events(response: httpx.Response) -> AsyncIterator[StreamEvent]:
    if response.status_code in (401, 403):
        await response.aread()
        raise AmaliaAuthError(
            f"Authentication failed (HTTP {response.status_code}). Check AMALIA_API_KEY."
        )
    if response.is_error:
        body = (await response.aread()).decode("utf-8", errors="replace")
        raise AmaliaHTTPError(response.status_code, body)

    async for line in response.aiter_lines():
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        yield StreamEvent(
            type=str(obj.get("type", "")),
            content=obj.get("content"),
            run_id=str(obj.get("run_id", "")),
            raw=obj,
        )


def _as_json_field(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _open_image(image: str | Path | IO[bytes]) -> tuple[IO[bytes] | None, tuple[str, IO[bytes]]]:
    if isinstance(image, (str, Path)):
        path = Path(image)
        fh = path.open("rb")
        return fh, (path.name, fh)
    name = getattr(image, "name", "image")
    return None, (Path(str(name)).name, image)

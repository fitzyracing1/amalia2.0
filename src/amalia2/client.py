"""
Amalia 2.0 Async Client (stub)
"""

from __future__ import annotations

from types import TracebackType
from typing import Any

import httpx
from pydantic import BaseModel
from typing_extensions import Self


class AmaliaConfig(BaseModel):
    base_url: str = "https://api.amaliallm.pt/v1"  # placeholder - update with real endpoint
    api_key: str | None = None
    timeout: float = 60.0


class AmaliaClient:
    """
    Modern async client for Amália LLM.
    """

    def __init__(
        self,
        config: AmaliaConfig | None = None,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.config = config or AmaliaConfig()
        headers = {"User-Agent": "amalia2/0.1.0"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers=headers,
            transport=transport,
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str = "amalia-9b",
        stream: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send a chat completion request."""
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs,
        }
        response = await self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return result

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

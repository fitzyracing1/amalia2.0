"""
Amalia 2.0 Async Client (stub)
"""

from __future__ import annotations

import os
from typing import Any, AsyncIterator, Optional

import httpx
from pydantic import BaseModel


class AmaliaConfig(BaseModel):
    base_url: str = "https://api.amaliallm.pt/v1"  # placeholder - update with real endpoint
    api_key: Optional[str] = None
    timeout: float = 60.0


class AmaliaClient:
    """
    Modern async client for Amália LLM.
    """

    def __init__(self, config: Optional[AmaliaConfig] = None):
        self.config = config or AmaliaConfig()
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers={
                "Authorization": f"Bearer {self.config.api_key}" if self.config.api_key else "",
                "User-Agent": "amalia2/0.1.0",
            },
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str = "amalia-9b",
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Send a chat completion request."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs,
        }
        response = await self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
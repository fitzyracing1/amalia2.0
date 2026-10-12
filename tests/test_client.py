"""Tests for amalia2.client using httpx.MockTransport (no network access)."""

from __future__ import annotations

import json
from collections.abc import Callable

import httpx
import pytest

from amalia2 import AmaliaClient
from amalia2.client import AmaliaConfig

OK_BODY = {
    "id": "chatcmpl-1",
    "object": "chat.completion",
    "model": "amalia-9b",
    "choices": [
        {
            "index": 0,
            "message": {"role": "assistant", "content": "Olá! Em que posso ajudar?"},
            "finish_reason": "stop",
        }
    ],
}

Handler = Callable[[httpx.Request], httpx.Response]


def make_client(
    config: AmaliaConfig | None = None,
    handler: Handler | None = None,
) -> tuple[AmaliaClient, list[httpx.Request]]:
    """Build a client whose transport records requests instead of hitting the network."""
    requests: list[httpx.Request] = []

    def default_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=OK_BODY)

    respond = handler or default_handler

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return respond(request)

    transport = httpx.MockTransport(recording_handler)
    return AmaliaClient(config, transport=transport), requests


async def test_chat_request_shape() -> None:
    client, requests = make_client()
    result = await client.chat(
        messages=[{"role": "user", "content": "Olá"}],
        temperature=0.2,
    )
    await client.close()

    assert result == OK_BODY
    (request,) = requests
    assert request.method == "POST"
    assert str(request.url) == "https://api.amaliallm.pt/v1/chat/completions"
    assert request.headers["content-type"] == "application/json"
    assert request.headers["user-agent"].startswith("amalia2/")
    payload = json.loads(request.content)
    assert payload == {
        "model": "amalia-9b",
        "messages": [{"role": "user", "content": "Olá"}],
        "stream": False,
        "temperature": 0.2,
    }


async def test_chat_custom_model_and_stream_flag() -> None:
    client, requests = make_client()
    await client.chat(
        messages=[{"role": "user", "content": "hi"}],
        model="amalia-9b-instruct",
        stream=True,
    )
    await client.close()
    payload = json.loads(requests[0].content)
    assert payload["model"] == "amalia-9b-instruct"
    assert payload["stream"] is True


async def test_auth_header_sent_when_api_key_set() -> None:
    config = AmaliaConfig(api_key="secret-key")
    client, requests = make_client(config)
    await client.chat(messages=[{"role": "user", "content": "hi"}])
    await client.close()
    assert requests[0].headers["authorization"] == "Bearer secret-key"


async def test_no_auth_header_without_api_key() -> None:
    client, requests = make_client()
    await client.chat(messages=[{"role": "user", "content": "hi"}])
    await client.close()
    assert "authorization" not in requests[0].headers


async def test_http_error_raises_status_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "invalid api key"})

    client, _ = make_client(handler=handler)
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        await client.chat(messages=[{"role": "user", "content": "hi"}])
    await client.close()
    assert excinfo.value.response.status_code == 401


async def test_unreachable_endpoint_raises_transport_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client, _ = make_client(handler=handler)
    with pytest.raises(httpx.ConnectError):
        await client.chat(messages=[{"role": "user", "content": "hi"}])
    await client.close()


async def test_context_manager_closes_client() -> None:
    client, _ = make_client()
    async with client as entered:
        assert entered is client
        assert not client._client.is_closed
    assert client._client.is_closed


async def test_custom_base_url_is_used() -> None:
    config = AmaliaConfig(base_url="http://localhost:8000/v1")
    client, requests = make_client(config)
    await client.chat(messages=[{"role": "user", "content": "hi"}])
    await client.close()
    assert str(requests[0].url) == "http://localhost:8000/v1/chat/completions"


def test_config_defaults() -> None:
    config = AmaliaConfig()
    assert config.base_url == "https://api.amaliallm.pt/v1"
    assert config.api_key is None
    assert config.timeout == 60.0

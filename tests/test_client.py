"""Tests for amalia2.client using httpx.MockTransport (no network access)."""

from __future__ import annotations

from collections.abc import Callable

import httpx
import pytest

from amalia2 import AmaliaAuthError, AmaliaClient, AmaliaError, AmaliaHTTPError, StreamEvent
from amalia2.client import USER_AGENT
from amalia2.config import DEFAULT_BASE_URL, AmaliaConfig

Handler = Callable[[httpx.Request], httpx.Response]

SAMPLE = AmaliaConfig(
    api_key="test-key",
    agent_id="agent-1",
    channel_id="channel-1",
)

NDJSON_OK = (
    b'{"type": "start", "content": "Processing", "run_id": "run-1"}\n'
    b'{"type": "token", "content": "Ol"}\n'
    b'{"type": "token", "content": "\xc3\xa1"}\n'
    b'{"type": "message", "content": {"content": "Ol\xc3\xa1", "model_name": "amalia",'
    b' "finish_reason": "stop"}}\n'
    b'{"type": "done", "content": "run-1", "messageId": "m1"}\n'
)

NDJSON_TOKENS_ONLY = (
    b'{"type": "token", "content": "Bom "}\n'
    b'{"type": "token", "content": "dia"}\n'
    b'{"type": "done", "content": "run-2"}\n'
)


def make_client(
    config: AmaliaConfig | None = None,
    handler: Handler | None = None,
) -> tuple[AmaliaClient, list[httpx.Request]]:
    """Build a client whose transport records requests instead of hitting the network."""
    requests: list[httpx.Request] = []

    def default_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=NDJSON_OK)

    respond = handler or default_handler

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return respond(request)

    transport = httpx.MockTransport(recording_handler)
    return AmaliaClient(config or SAMPLE, transport=transport), requests


def _body_text(request: httpx.Request) -> str:
    return request.content.decode("utf-8", errors="replace")


async def test_stream_parses_ndjson_events() -> None:
    client, requests = make_client()
    events = [ev async for ev in client.stream("Olá", thread_id="thread-1")]
    await client.close()

    assert [ev.type for ev in events] == ["start", "token", "token", "message", "done"]
    assert events[1] == StreamEvent(
        type="token",
        content="Ol",
        run_id="",
        raw={"type": "token", "content": "Ol"},
    )
    assert events[2].content == "á"
    message = events[3].content
    assert isinstance(message, dict)
    assert message["content"] == "Olá"
    assert events[0].run_id == "run-1"

    (request,) = requests
    assert request.method == "POST"
    assert str(request.url) == (
        f"{DEFAULT_BASE_URL}//api/v1/agent/{SAMPLE.agent_id}/stream"
    )
    assert request.headers["x-api-key"] == "test-key"
    assert request.headers["user-agent"] == USER_AGENT
    assert request.headers["content-type"].startswith("multipart/form-data")
    body = _body_text(request)
    assert "channel_id" in body
    assert SAMPLE.channel_id in body
    assert "thread-1" in body
    assert "Olá" in body


async def test_complete_prefers_message_event() -> None:
    client, _ = make_client()
    reply = await client.complete("Olá", thread_id="t")
    await client.close()
    assert reply == "Olá"


async def test_complete_falls_back_to_concatenated_tokens() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=NDJSON_TOKENS_ONLY)

    client, _ = make_client(handler=handler)
    reply = await client.complete("hi", thread_id="t")
    await client.close()
    assert reply == "Bom dia"


async def test_skips_malformed_ndjson_lines() -> None:
    payload = (
        b"not-json\n"
        b'{"type": "token", "content": "ok"}\n'
        b"\n"
        b'{"type": "done", "content": "x"}\n'
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=payload)

    client, _ = make_client(handler=handler)
    events = [ev async for ev in client.stream("x", thread_id="t")]
    await client.close()
    assert [ev.type for ev in events] == ["token", "done"]
    assert events[0].content == "ok"


async def test_auth_failure_raises_typed_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "invalid api key"})

    client, _ = make_client(handler=handler)
    with pytest.raises(AmaliaAuthError, match="AMALIA_API_KEY"):
        async for _ in client.stream("hi", thread_id="t"):
            pass
    await client.close()


async def test_forbidden_raises_auth_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="nope")

    client, _ = make_client(handler=handler)
    with pytest.raises(AmaliaAuthError, match="403"):
        await client.complete("hi", thread_id="t")
    await client.close()


async def test_http_error_exposes_status_and_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="upstream exploded")

    client, _ = make_client(handler=handler)
    with pytest.raises(AmaliaHTTPError) as excinfo:
        await client.complete("hi", thread_id="t")
    await client.close()
    assert excinfo.value.status_code == 500
    assert "upstream exploded" in excinfo.value.body


async def test_unreachable_endpoint_raises_amalia_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client, _ = make_client(handler=handler)
    with pytest.raises(AmaliaError, match="Network error"):
        await client.complete("hi", thread_id="t")
    await client.close()


async def test_context_manager_closes_client() -> None:
    client, _ = make_client()
    async with client as entered:
        assert entered is client
        assert not client._client.is_closed
    assert client._client.is_closed


async def test_custom_base_url_is_used() -> None:
    config = AmaliaConfig(
        api_key="k",
        agent_id="ag",
        channel_id="ch",
        base_url="http://localhost:8000/agent-chat/",
    )
    client, requests = make_client(config)
    await client.complete("hi", thread_id="t")
    await client.close()
    assert str(requests[0].url) == "http://localhost:8000/agent-chat//api/v1/agent/ag/stream"


async def test_optional_fields_are_sent() -> None:
    client, requests = make_client()
    await client.complete(
        "hi",
        thread_id="t",
        user_id="user-9",
        user_info={"name": "Ana"},
        user_context={"locale": "pt-PT"},
    )
    await client.close()
    body = _body_text(requests[0])
    assert "user-9" in body
    assert "Ana" in body
    assert "pt-PT" in body


def test_config_stream_url_and_defaults() -> None:
    config = AmaliaConfig(api_key="k", agent_id="ag", channel_id="ch")
    assert config.base_url == DEFAULT_BASE_URL
    assert config.timeout == 120.0
    assert config.stream_url() == f"{DEFAULT_BASE_URL}//api/v1/agent/ag/stream"


def test_new_thread_id_is_url_safe() -> None:
    tid = AmaliaClient.new_thread_id()
    assert len(tid) >= 8
    assert "/" not in tid

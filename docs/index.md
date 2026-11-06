# Amalia 2.0

Amalia 2.0 is an early-stage (v0.1.0-alpha) Python SDK and CLI for Amália, the Portuguese (pt-PT) LLM from the AMALIA-LLM initiative. The original SDK is [alfmatos/amalia](https://github.com/alfmatos/amalia).

**Current state, from the code:**
- `AmaliaClient` is an async `httpx` client for the IAEdu agent-chat API (`https://api.iaedu.pt/agent-chat`).
- `stream()` yields NDJSON events (`start` / `token` / `message` / `done`); `complete()` returns the aggregated reply.
- Auth is `x-api-key`. Config comes from `AMALIA_API_KEY`, `AMALIA_AGENT_ID`, `AMALIA_CHANNEL_ID` (optional `AMALIA_BASE_URL`) or `creds.txt`.
- `amalia2 chat` is an interactive Rich session that streams tokens. It fails clearly if credentials are missing.
- `amalia2 new` is still a stub (scaffolding is phase 03).
- Tests use `httpx.MockTransport` — no live network or secrets. CI runs ruff, mypy (strict), and pytest.
- The package is not on PyPI: `pip install amalia2` is still planned.

Pages: [Getting started](getting-started.md) · [Usage](usage.md) · [Architecture](architecture.md) · [Contributing](contributing.md)

MIT License. Copyright (c) 2026 Joshua Almeida

# Amalia 2.0

Amalia 2.0 is an early-stage (v0.1.0-alpha) Python SDK and CLI for Amália, the Portuguese (pt-PT) LLM from the AMALIA-LLM initiative. The original SDK is [alfmatos/amalia](https://github.com/alfmatos/amalia).

**Current state, from the code:**
- `AmaliaClient` is an async `httpx` client with one `chat()` method that POSTs to `/chat/completions`.
- The default `base_url` (`https://api.amaliallm.pt/v1`) is marked in the source as a **placeholder**. The real endpoint has not been confirmed.
- The CLI commands `chat` and `new` are **stubs** that only print messages.
- There are no tests or CI yet. The package is not on PyPI: the README lists `pip install amalia2` as "planned".

Pages: [Getting started](getting-started.md) · [Usage](usage.md) · [Architecture](architecture.md) · [Contributing](contributing.md)

The README states MIT, but the repo has no LICENSE file. Copyright (c) 2026 Joshua Almeida

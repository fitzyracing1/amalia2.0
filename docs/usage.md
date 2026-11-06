# Usage

## Python API

Config (`src/amalia2/config.py`):

- `AmaliaConfig(api_key, agent_id, channel_id, base_url="https://api.iaedu.pt/agent-chat", timeout=120.0)`
- `load_config()` reads `AMALIA_API_KEY`, `AMALIA_AGENT_ID`, `AMALIA_CHANNEL_ID`, optional `AMALIA_BASE_URL`, then falls back to `./creds.txt` or `~/.amalia/creds.txt`.
- Auth header is `x-api-key` (not `Authorization: Bearer`).
- Stream URL is `{base}//api/v1/agent/{agent_id}/stream` (the double slash matches the official IAEdu example).

Client (`src/amalia2/client.py`):

- `AmaliaClient(config=None, transport=None)` — async context manager. If `config` is omitted, calls `load_config()`.
- `async stream(message, *, thread_id, ...)` yields `StreamEvent` (`start` | `token` | `message` | `done`) from the NDJSON body.
- `async complete(message, *, thread_id, ...)` → aggregated reply string (prefers the `message` event, else concatenated tokens).
- `new_thread_id()` — reuse the same id across turns for server-side memory.

Errors: `AmaliaAuthError` (401/403), `AmaliaHTTPError` (other non-2xx, with `.status_code` and `.body`), `AmaliaError` (missing config or network).

## CLI (`amalia2`, Typer)

| Command | Status |
|---|---|
| `amalia2 version` | prints the version |
| `amalia2 chat [-s SYSTEM] [--thread ID]` | interactive Rich session; streams tokens. Exits with code 1 if credentials are missing |
| `amalia2 new NAME [-t basic]` | stub: prints a message, no scaffolding yet (phase 03 follow-up) |

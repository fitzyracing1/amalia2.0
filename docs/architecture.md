# Architecture

| Path | Role |
|---|---|
| `src/amalia2/__init__.py` | version, public exports |
| `src/amalia2/config.py` | `AmaliaConfig` (pydantic) and `load_config()` (env + creds.txt) |
| `src/amalia2/errors.py` | `AmaliaError`, `AmaliaAuthError`, `AmaliaHTTPError` |
| `src/amalia2/client.py` | async `httpx` IAEdu client: `stream()`, `complete()`, `StreamEvent` |
| `src/amalia2/cli.py` | Typer app, entry point `amalia2 = amalia2.cli:main` |
| `examples/basic_chat.py` | minimal async streaming example |
| `docs/index.html` | website |
| `pyproject.toml` | hatchling build. Ruff line length is 100, and mypy runs in strict mode |

The IAEdu agent-chat API is the primary transport. Conversation memory is per-`thread_id` on the server. Shape reference: [alfmatos/amalia](https://github.com/alfmatos/amalia) (`amalia-sdk`).

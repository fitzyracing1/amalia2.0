# Usage

## Python API (`src/amalia2/client.py`)
- `AmaliaConfig(base_url="https://api.amaliallm.pt/v1", api_key=None, timeout=60.0)`. When `api_key` is set it is sent as `Authorization: Bearer ...`.
- `AmaliaClient(config=None)` provides `async chat(messages, model="amalia-9b", stream=False, **kwargs)` → parsed JSON, plus `close()`. It also works as an async context manager.

Pass the key through the config object, for example from an environment variable you choose. Do not hard-code it.

## CLI (`amalia2`, Typer)
| Command | Status |
|---|---|
| `amalia2 version` | prints the version |
| `amalia2 chat [-m amalia-9b] [-s SYSTEM]` | stub: prints a placeholder panel |
| `amalia2 new NAME [-t basic]` | stub: prints a message, no scaffolding yet |

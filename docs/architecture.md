# Architecture

| Path | Role |
|---|---|
| `src/amalia2/__init__.py` | version, exports `AmaliaClient` |
| `src/amalia2/client.py` | `AmaliaConfig` (pydantic) and `AmaliaClient` (httpx) |
| `src/amalia2/cli.py` | Typer app, entry point `amalia2 = amalia2.cli:main` |
| `examples/basic_chat.py` | minimal async chat example |
| `docs/index.html` | website |
| `pyproject.toml` | hatchling build. Ruff line length is 100, and mypy runs in strict mode |

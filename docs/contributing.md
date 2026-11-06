# Contributing

```bash
pip install -e '.[dev]'
ruff check .
mypy src
pytest -v
```

CI runs ruff, mypy (strict), and pytest on Python 3.10 and 3.12. Do not commit API keys or `creds.txt`. Tests must use `httpx.MockTransport` (no live network).

Useful follow-ups: implement `amalia2 new` project scaffolding (phase 03).

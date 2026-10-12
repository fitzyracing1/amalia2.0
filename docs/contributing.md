# Contributing

```bash
pip install -e '.[dev]'
ruff check .
mypy src
```

There are no tests yet (pytest is listed in `dev`). Useful next steps visible in the code: confirm the real API endpoint, and implement the `chat` and `new` CLI commands.

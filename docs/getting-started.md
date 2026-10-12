# Getting started

Requires Python ≥ 3.10. Install from source, since the package is not published:

```bash
git clone https://github.com/fitzyracing1/Amalia2.0 && cd Amalia2.0
pip install -e .            # extras: .[chat], .[agents], .[dev]
amalia2 version
```

Example (`examples/basic_chat.py`). It needs a reachable endpoint, and the default URL is a placeholder:

```python
import asyncio
from amalia2 import AmaliaClient

async def main():
    async with AmaliaClient() as client:
        print(await client.chat(messages=[{"role": "user", "content": "Olá!"}], model="amalia-9b"))

asyncio.run(main())
```

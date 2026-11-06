# Getting started

Requires Python ≥ 3.10. Install from source, since the package is not published:

```bash
git clone https://github.com/fitzyracing1/amalia2.0 && cd amalia2.0
pip install -e .            # extras: .[chat], .[agents], .[dev]
amalia2 version
```

## Credentials

The live Amália API is IAEdu agent-chat (not OpenAI `/chat/completions`). Set:

```bash
export AMALIA_API_KEY=sk-usr-...
export AMALIA_AGENT_ID=<your-agent-id>
export AMALIA_CHANNEL_ID=<your-channel-id>
# optional, only if you are on a different deployment:
# export AMALIA_BASE_URL=https://api.iaedu.pt/agent-chat
```

Request a key, agent id, and channel id from [iaedu.pt](https://iaedu.pt/pt). Alternatively, place a `creds.txt` (the format your account ships with) in the current directory or at `~/.amalia/creds.txt`:

```
Endpoint: https://api.iaedu.pt/agent-chat//api/v1/agent/<your-agent-id>/stream
API Key: sk-usr-...
ChannelID: <your-channel-id>
```

Env vars take precedence. Never commit `creds.txt`.

Then:

```bash
amalia2 chat
```

## Python

Example (`examples/basic_chat.py`):

```python
import asyncio
from amalia2 import AmaliaClient, load_config

async def main():
    async with AmaliaClient(load_config()) as client:
        thread = client.new_thread_id()
        print(await client.complete("Olá!", thread_id=thread))

asyncio.run(main())
```

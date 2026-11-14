"""Basic streaming chat example with Amalia 2.0 (IAEdu agent API)."""

from __future__ import annotations

import asyncio

from amalia2 import AmaliaClient, load_config


async def main() -> None:
    async with AmaliaClient(load_config()) as client:
        thread = client.new_thread_id()
        async for ev in client.stream("Olá! Como estás hoje?", thread_id=thread):
            if ev.type == "token" and isinstance(ev.content, str):
                print(ev.content, end="", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(main())

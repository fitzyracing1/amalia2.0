"""
Basic chat example with Amalia 2.0
"""

import asyncio
from amalia2 import AmaliaClient


async def main():
    async with AmaliaClient() as client:
        response = await client.chat(
            messages=[
                {"role": "user", "content": "Olá! Como estás hoje?"}
            ],
            model="amalia-9b"
        )
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
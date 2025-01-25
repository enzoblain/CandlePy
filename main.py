# Local Imports
from src.algo import algo
from src.api import api

# External imports
import asyncio

async def main():
    await asyncio.gather(algo(), api())

if __name__ == "__main__":
    asyncio.run(main())
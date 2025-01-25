# External imports
import asyncio

async def algo():
    for i in range(10, 0, -1):
        print(i)
        await asyncio.sleep(1)

    raise Exception("Boom!")
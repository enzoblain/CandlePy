# External imports
import asyncio

async def algo(window: classmethod):
    for i in range(10, 0, -1):
        print(i)
        await asyncio.sleep(1)

    print("Boom!")

    await window.signal_quit()
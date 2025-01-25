# External imports
import asyncio

async def algo(window: classmethod):
    for i in range(100):
        candle = {
                "information": True,
                "open": i,
                "close": 0,
                "high": 0,
                "low": 0,
                "x_start": 0,
                "x_end": 0
            }
        window.addCandle(candle)

        await asyncio.sleep(0.1)

    return


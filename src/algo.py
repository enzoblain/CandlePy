# External imports
import asyncio

async def algo(window: classmethod):
    for i in range(100):
        candle = {
                "information": True,
                "open": 0,
                "close": 0,
                "high": i,
                "low": 0.8 * i,
                "x_start": 0,
                "x_end": 0
            }
        window.addCandle(candle)

        await asyncio.sleep(1)

    return


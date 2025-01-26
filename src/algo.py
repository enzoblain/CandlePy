import asyncio
import numpy as np
import pandas as pd
import sdl2

async def algo(window: classmethod):
    data = pd.read_csv("data/candles.csv")

    data["direction"] = np.where(data["close"] > data["open"], "Bullish", "Bearish")
    data["information"] = True

    paused = False  # Pause state
    i = 0  # Current data index

    while i < len(data):
        if not window.paused:
            window.addCandle(data.iloc[i])
            i += 1
            await asyncio.sleep(0.2)
        else:
            await asyncio.sleep(0.1)


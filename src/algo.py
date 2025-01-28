# External imports
import asyncio
import numpy as np
import pandas as pd

async def algo(window: object) -> None:
    data = pd.read_csv("data/candles.csv")

    data["direction"] = np.where(data["close"] > data["open"], "Bullish", "Bearish")

    i = 0

    while i < len(data):
        if not window.paused:
            window.addCandle(data.iloc[i])

            i += 1

            await asyncio.sleep(0.2)

        else:
            await asyncio.sleep(0.1)
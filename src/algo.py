import asyncio
import numpy as np
import pandas as pd

async def algo(window: classmethod):
    data = pd.read_csv("data/candles.csv")

    data["direction"] = np.where(data["close"] > data["open"], "Bullish", "Bearish")
    data["information"] = True

    for i in range(len(data)):
        window.addCandle(data.iloc[i])

        await asyncio.sleep(0.2)

    return


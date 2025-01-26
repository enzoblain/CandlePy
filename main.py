from src.algo import algo
from src.api import SDL2Window

import asyncio
import json

async def main():
    config = json.load(open("config.json"))
    theme = json.load(open("themes.json"))[config["Theme"]]

    window = SDL2Window(title="Trading Chart", size=(800, 600), grid_size=15, margin = (15, 20), theme=theme)
    
    window_task = asyncio.create_task(window.run())
    algo_task = asyncio.create_task(algo(window))
    
    try:
        await asyncio.gather(window_task, algo_task)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

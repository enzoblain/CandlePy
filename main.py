# Local imports 
from src.algo import algo # Function giving the candles data
from src.api import SDL2Window # Function showing the chart

# External imports
import asyncio
import json

async def main() -> None:
    config = json.load(open("config.json"))
    theme = json.load(open("themes.json"))[config["Theme"]]

    window = SDL2Window(title="Trading Chart", size=(800, 600), column_width=15, margin=(15, 20), theme=theme) # Create the window object
    
    window_task = asyncio.create_task(window.run())
    algo_task = asyncio.create_task(algo(window))
    
    try:
        await asyncio.gather(window_task, algo_task)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

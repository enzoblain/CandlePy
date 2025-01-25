# Local Imports
from src.algo import algo
from src.api import SDL2Window

# External imports
import asyncio

async def main():
    window = SDL2Window(title="Trading Chart", size=(800, 600))
    _ = asyncio.create_task(window.run())

    try:
        while True:
            await algo(window)
            await asyncio.sleep(60)

    except Exception as e:
        raise e
    
    window.signal_quit()

if __name__ == "__main__":
    asyncio.run(main())
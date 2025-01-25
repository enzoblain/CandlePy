# External imports
import asyncio
import pandas as pd
import numpy as np
import sdl2
import sdl2.ext

class SDL2Window:
    def __init__(self, title="PySDL2 Window", size=(800, 600), grid_size=15, margin=(15, 20)):
        self.title = title
        self.size = size
        self.grid_size = grid_size
        self.window = None
        self.running = False
        self.renderer = None
        self.margin = margin
        self.grid_y = (0 + margin[0], size[1] - margin[0])
        self.grid_y_length = self.grid_y[1] - self.grid_y[0]
        self.data_max = 0
        self.data_min = 0
        self.data_length = 0

        self.quit_event = asyncio.Event()  # Event to signal the window to quit

        self.cols = round((size[0] * 0.8) // grid_size) # Number of candles that can fit in the window, leaving a right margin of 20%

        candles_dict = {
            "information": [False] * self.cols,
            "open": [0] * self.cols,
            "close": [0] * self.cols,
            "high": [0] * self.cols,
            "low": [0] * self.cols,
            "x_start": [0] * self.cols,
            "x_end": [0] * self.cols,
            "y_start": [0] * self.cols,
            "y_end": [0] * self.cols
        }

        self.candles = pd.DataFrame(candles_dict)

        self.getCandlesXCoord()

    async def init(self):
        """Initialize SDL2 and create a window."""
        try:
            sdl2.ext.init()

            self.window = sdl2.ext.Window(self.title, size=self.size)
            self.window.show()

            self.renderer = sdl2.ext.Renderer(self.window)
            self.running = True

            print(f"SDL2 initialized, window created with size: {self.size}")

        except Exception as e:
            print(f"Error initializing SDL2: {e}")

    async def handle_events(self):
        """Handle events within the window."""
        events = sdl2.ext.get_events()

        for event in events:
            if event.type == sdl2.SDL_QUIT:
                self.running = False
                
                asyncio.Task.cancel()

    async def run(self):
        """Run the event loop."""
        await self.init()

        while self.running:
            await self.handle_events()

            self.renderer.clear() # Clear the window

            self.renderer.present() # Update the window

            await asyncio.sleep(0.01)

        await self.quit()

    def addCandle(self, candle: dict):
        """Add a candle to the chart."""

        filtered_candles = self.candles[self.candles["information"] == True] # Get the candles with information

        self.updataDataChars(candle)

        if not filtered_candles.empty: # If there is a candle with information
            last_candle_index = filtered_candles.index[-1]

            if last_candle_index == self.cols - 1: # If the dataframe is full of candles with information
                candle = pd.DataFrame([candle])

                self.candles = self.candles.drop(index=0).reset_index(drop=True) # Remove the first candle from the dataframe
                self.candles = pd.concat([self.candles, candle], ignore_index=True) # Add the candle to the dataframe on the last position

            else: # If the dataframe is not full of candles with information
                self.candles.loc[last_candle_index + 1] = candle # Add the candle to the dataframe on the next position
            
        else: # If there is no candle with information
            candle = pd.DataFrame([candle])

            self.candles = self.candles.drop(index=0).reset_index(drop=True) # Remove the first candle from the dataframe
            self.candles = pd.concat([candle, self.candles], ignore_index=True) # Add the candle to the dataframe on the first position

        self.getCandlesXCoord()
        self.getCandlesYCoord()

        print(self.candles)

    def getCandlesXCoord(self):
        """Define the x-coordinates of the candles."""
        self.candles["x_start"] = np.arange(0, len(self.candles) * self.grid_size, self.grid_size)
        self.candles["x_start"] = self.margin[0] + self.candles["x_start"]
        self.candles["x_end"] = self.candles["x_start"] + self.grid_size

    def updataDataChars(self, candle: dict):
        """Update the information of the candle."""
        changes = False

        if candle["high"] > self.data_max:
            self.data_max = candle["high"]
            changes = True
        
        if candle["low"] < self.data_min:
            self.data_min = candle["low"]
            changes = True

        if changes:
            self.data_length = self.data_max - self.data_min

    def getCandlesYCoord(self):
        """Define the y-coordinates of the candles."""
        # Create a mask for candles where information is True
        mask = self.candles['information'] == True

        # Apply the calculation to only those rows where the condition is True to minimize the number of calculations
        self.candles.loc[mask, 'y_start'] = self.grid_y[0] + (self.candles.loc[mask, 'low'] - self.data_min) * self.grid_y_length / self.data_length
        self.candles.loc[mask, 'y_end'] = self.grid_y[0] + (self.candles.loc[mask, 'high'] - self.data_min) * self.grid_y_length / self.data_length


    async def quit(self):
        """Cleanup, close the window, and quit SDL2."""
        if self.window:
            self.window.close()  

        sdl2.ext.quit()

    def signal_quit(self):
        """Signal the window to quit the event loop."""
        self.running = False
        self.quit_event.set()
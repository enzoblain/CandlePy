import asyncio
import pandas as pd
import numpy as np
import sdl2
import sdl2.ext

class SDL2Window:
    def __init__(self, title="PySDL2 Window", size=(800, 600), grid_size=15, margin=(15, 20), theme=None):
        self.title = title
        self.size = size
        self.grid_size = grid_size
        self.window = None
        self.running = False
        self.renderer = None
        self.sdl_renderer = None
        self.margin = margin
        self.grid_y = (0 + margin[0], size[1] - margin[0])
        self.grid_y_length = self.grid_y[1] - self.grid_y[0]
        self.data_max = 0
        self.data_min = 0
        self.data_length = 0
        self.quit_event = asyncio.Event()
        self.cols = round((size[0] * 0.8) // grid_size)
        self.theme = theme

        candles_dict = {
            "information": [False] * self.cols,
            "open": [0] * self.cols,
            "close": [0] * self.cols,
            "high": [0] * self.cols,
            "low": [0] * self.cols,
            "x_start": [0] * self.cols,
            "x_center": [0] * self.cols,
            "x_end": [0] * self.cols,
            "y_body_start": [0] * self.cols,
            "y_body_end": [0] * self.cols,
            "y_wick_high": [0] * self.cols,
            "y_wick_low": [0] * self.cols,
        }

        self.candles = pd.DataFrame(candles_dict)
        self.getCandlesXCoord()

    async def init(self):
        try:
            sdl2.ext.init()

            self.window = sdl2.ext.Window(self.title, size=self.size)
            self.window.show()
            self.renderer = sdl2.ext.Renderer(self.window)
            self.sdl_renderer = self.renderer.renderer
            self.running = True

            print(f"SDL2 initialized, window created with size: {self.size}")

        except Exception as e:
            print(f"Error initializing SDL2: {e}")

    async def handle_events(self):
        events = sdl2.ext.get_events()

        for event in events:
            if event.type == sdl2.SDL_QUIT:
                self.running = False
                
                asyncio.Task.cancel()

    async def run(self):
        await self.init()

        while self.running:
            await self.handle_events()
            await asyncio.sleep(0.01)

        await self.quit()

    def addCandle(self, candle: dict):
        filtered_candles = self.candles[self.candles["information"] == True]

        candle = pd.DataFrame([candle])

        if not filtered_candles.empty:
            last_candle_index = filtered_candles.index[-1]

            if last_candle_index == self.cols - 1:
                self.candles = self.candles.drop(index=0).reset_index(drop=True)
                self.candles = pd.concat([self.candles, candle], ignore_index=True)

            else:
                self.candles.loc[last_candle_index + 1] = candle.iloc[0]
            
        else:
            self.candles = self.candles.drop(index=0).reset_index(drop=True)
            self.candles = pd.concat([candle, self.candles], ignore_index=True)

        self.updataDateChars()
        self.getCandlesXCoord()
        self.getCandlesYCoord()
        self.drawCandles()

    def getCandlesXCoord(self):
        self.candles["x_start"] = np.arange(0, len(self.candles) * self.grid_size, self.grid_size)
        self.candles["x_start"] = self.margin[0] + self.candles["x_start"]
        self.candles["x_center"] = self.candles["x_start"] + self.grid_size // 2 + 1
        self.candles["x_end"] = self.candles["x_start"] + self.grid_size

    def updataDateChars(self):
        mask = self.candles['information'] == True

        self.data_max = self.candles.loc[mask, "high"].max()
        self.data_min = self.candles.loc[mask, "low"].min()
        self.data_length = self.data_max - self.data_min

    def getCandlesYCoord(self):
        mask = self.candles['information'] == True

        self.candles.loc[mask, 'y_body_start'] = self.grid_y[1] - round(
            (self.candles.loc[mask, ['open', 'close']].min(axis=1) - self.data_min) * self.grid_y_length / self.data_length
        )
        self.candles.loc[mask, 'y_body_end'] = self.grid_y[1] - round(
            (self.candles.loc[mask, ['open', 'close']].max(axis=1) - self.data_min) * self.grid_y_length / self.data_length
        )

        self.candles.loc[mask, 'y_wick_high'] = self.grid_y[1] - round(
            (self.candles.loc[mask, 'high'] - self.data_min) * self.grid_y_length / self.data_length
        )
        self.candles.loc[mask, 'y_wick_low'] = self.grid_y[1] - round(
            (self.candles.loc[mask, 'low'] - self.data_min) * self.grid_y_length / self.data_length
        )

    def drawRectangle(self, x_start, y_start, x_end, y_end, color):
        rectangle = sdl2.SDL_Rect(
            int(x_start),
            int(y_start),
            int(x_end - x_start),
            int(y_end - y_start)
        )

        sdl2.SDL_SetRenderDrawColor(self.sdl_renderer, color[0], color[1], color[2], 255)
        sdl2.SDL_RenderFillRect(self.sdl_renderer, rectangle)

    def drawLine(self, x, y_start, y_end, color):
        sdl2.SDL_SetRenderDrawColor(self.sdl_renderer, color[0], color[1], color[2], 255)
        sdl2.SDL_RenderDrawLine(self.sdl_renderer, int(x), int(y_start), int(x), int(y_end))

    def drawCandles(self):
        sdl2.SDL_SetRenderDrawColor(self.sdl_renderer, *self.theme["Background"])
        sdl2.SDL_RenderClear(self.sdl_renderer)

        for i in range(len(self.candles)):
            candle = self.candles.iloc[i]

            if candle["information"]:
                if candle["direction"] == "Bullish":
                    self.drawRectangle(candle["x_start"], candle["y_body_start"], candle["x_end"], candle["y_body_end"], self.theme["Candle"]["Bullish"])
                    self.drawLine(candle["x_center"], candle["y_wick_high"], candle["y_wick_low"], self.theme["Candle"]["Bullish"])
                else:
                    self.drawRectangle(candle["x_start"], candle["y_body_start"], candle["x_end"], candle["y_body_end"], self.theme["Candle"]["Bearish"])
                    self.drawLine(candle["x_center"], candle["y_wick_high"], candle["y_wick_low"], self.theme["Candle"]["Bearish"])

        sdl2.SDL_RenderPresent(self.sdl_renderer)

    async def quit(self):
        if self.window:
            self.window.close()  

        sdl2.ext.quit()

    def signal_quit(self):
        """Signal the window to quit the event loop."""
        self.running = False
        self.quit_event.set()
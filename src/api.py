import asyncio
import pandas as pd
import numpy as np
import sdl2
import sdl2.ext
from PIL import Image
from ctypes import cast, POINTER, c_ubyte
from datetime import datetime

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
        self.paused = False

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

            if event.type == sdl2.SDL_KEYDOWN and event.key.keysym.sym == sdl2.SDLK_SPACE:
                self.paused = not self.paused

            if event.type == sdl2.SDL_KEYDOWN and event.key.keysym.sym == sdl2.SDLK_RETURN:
                self.screenShot()

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

    def screenShot(self, filename=None):
        try:
            surface = sdl2.SDL_CreateRGBSurface(
                0,  # flags
                self.size[0],  # width
                self.size[1],  # height
                32,  # depth
                0x00FF0000,  # Rmask
                0x0000FF00,  # Gmask
                0x000000FF,  # Bmask
                0xFF000000   # Amask
            )
            
            if not surface:
                print(f"Error creating surface: {sdl2.SDL_GetError().decode()}")
                return

            if sdl2.SDL_RenderReadPixels(
                self.sdl_renderer,
                None,  # rect=None means entire renderer
                surface.contents.format.contents.format,
                surface.contents.pixels,
                surface.contents.pitch
            ) < 0:
                print(f"Error reading pixels: {sdl2.SDL_GetError().decode()}")
                sdl2.SDL_FreeSurface(surface)
                return

            pixels = cast(surface.contents.pixels, POINTER(c_ubyte))
            pixel_data = bytes(pixels[: self.size[0] * self.size[1] * 4])
            
            image = Image.frombytes(
                'RGBA',
                self.size,
                pixel_data,
                'raw',
                'BGRA'  
            )

            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"

            image.save(filename)

            sdl2.SDL_FreeSurface(surface)

        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")

    async def quit(self):
        if self.window:
            self.window.close()  

        sdl2.ext.quit()

    def signal_quit(self):
        """Signal the window to quit the event loop."""
        self.running = False
        self.quit_event.set()
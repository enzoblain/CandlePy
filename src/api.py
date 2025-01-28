# External imports
import asyncio
import numpy as np
import pandas as pd
import sdl2
import sdl2.ext

from ctypes import cast, POINTER, c_ubyte
from datetime import datetime
from PIL import Image
from typing import Tuple

class SDL2Window:
    def __init__(self: object, 
                 title: str = "PySDL2 Window", 
                 size : Tuple[int, int] = (800, 600), 
                 column_width: int = 15, 
                 margin : Tuple[int, int] = (15, 20), 
                 theme : dict = None) -> None:
        """
        Initialize the SDL2 window
        :param title: The title of the window
        :param size: The size of the window (width, height)
        :param column_width: The width of each candlestick
        :param margin: The margin of the window
        :param theme: The theme of the window
        """
        self.title = title
        self.theme = theme

        self.size = size
        self.margin = margin
        self.grid_y_size = (0 + self.margin[1], size[1] - self.margin[1]) # Y axis range for the chart
        self.grid_y_length = self.grid_y_size[1] - self.grid_y_size[0] # Length of the chart's Y axis
        self.column_width = column_width # Number of columns in the chart
        self.cols = round((size[0] * 0.8) // self.column_width) # Number of columns that fit in the chart

        self.window = None
        self.running = False
        self.renderer = None
        self.sdl_renderer = None
        self.quit_event = asyncio.Event()
        self.paused = False

        self.data_max = 0
        self.data_min = 0
        self.data_length = 0

        # Create a DataFrame to store the candles that will be displayed
        candles_dict = {
            "datetime": [0] * self.cols,
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

    async def init(self: object) -> None:
        """
        Initialize the SDL2 window
        """
        try:
            sdl2.ext.init()

            self.window = sdl2.ext.Window(self.title, size=self.size)
            self.window.show()

            self.renderer = sdl2.ext.Renderer(self.window)
            self.sdl_renderer = self.renderer.renderer

            self.running = True

        except Exception as e:
            print(f"Error initializing SDL2: {e}")

    async def handle_events(self: object) -> None:
        """
        Handle the events of the SDL2 window
        """
        events = sdl2.ext.get_events()

        for event in events:
            if event.type == sdl2.SDL_QUIT:
                self.running = False

                asyncio.Task.cancel()

            if event.type == sdl2.SDL_KEYDOWN and event.key.keysym.sym == sdl2.SDLK_SPACE: # If the space key is pressed, pause the chart
                self.paused = not self.paused

            if event.type == sdl2.SDL_KEYDOWN and event.key.keysym.sym == sdl2.SDLK_RETURN: # If the return key is pressed, take a screenshot
                self.screenShot()

    async def run(self: object) -> None:
        """
        Run the SDL2 window
        """
        await self.init()

        while self.running:
            await self.handle_events()

            await asyncio.sleep(0.01)

        await self.quit()

    def addCandle(self: object, candle: dict) -> None:
        """
        Add a candle to the chart
        :param candle: The candle to be added
        """
        filtered_candles = self.candles[self.candles["datetime"] != 0] # Filter the part of the DataFrame that contains candles

        candle = pd.DataFrame([candle])

        if not filtered_candles.empty: # If the DataFrame contains candles
            last_candle_index = filtered_candles.index[-1] # Get the index of the last candle

            if last_candle_index == self.cols - 1: # If the DataFrame is full of candles
                self.candles = self.candles.drop(index=0).reset_index(drop=True) # Drop the first candle
                self.candles = pd.concat([self.candles, candle], ignore_index=True) # Add the new candle to the DataFrame

            else: # If the DataFrame is not full of candles
                self.candles.loc[last_candle_index + 1] = candle.iloc[0] # Add the new candle to the DataFrame after the last candle
            
        else: # If the DataFrame does not contain candles
            self.candles.loc[0] = candle.iloc[0] # Add the new candle to the DataFrame at the first position

        self.updataDateChars()
        self.getCandlesXCoord()
        self.getCandlesYCoord()
        self.drawCandles()

    def getCandlesXCoord(self: object) -> None:
        """
        Get the X coordinates of the candles relatively to their size
        """
        self.candles["x_start"] = self.margin[0] + np.arange(0, len(self.candles) * self.column_width, self.column_width) 
        self.candles["x_center"] = self.candles["x_start"] + self.column_width // 2 + 1
        self.candles["x_end"] = self.candles["x_start"] + self.column_width

    def updataDateChars(self: object) -> None:
        mask = self.candles['datetime'] != 0 # Filter the part of the DataFrame that contains candles

        self.data_max = self.candles.loc[mask, "high"].max()
        self.data_min = self.candles.loc[mask, "low"].min() 

        self.data_length = self.data_max - self.data_min # Get the price range of the candles

    def getCandlesYCoord(self: object) -> None:
        """
        Get the Y coordinates of the candles relatively to the price range
        """
        mask = self.candles['datetime'] != 0 # Filter the part of the DataFrame that contains candles

        self.candles.loc[mask, 'y_body_start'] = self.grid_y_size[1] - round(
            (self.candles.loc[mask, ['open', 'close']].min(axis=1) - self.data_min) * self.grid_y_length / self.data_length
        ) # Get the Y coordinate of the body's start relatively to the price range
        self.candles.loc[mask, 'y_body_end'] = self.grid_y_size[1] - round(
            (self.candles.loc[mask, ['open', 'close']].max(axis=1) - self.data_min) * self.grid_y_length / self.data_length
        ) # Get the Y coordinate of the body's end relatively to the price range

        self.candles.loc[mask, 'y_wick_high'] = self.grid_y_size[1] - round(
            (self.candles.loc[mask, 'high'] - self.data_min) * self.grid_y_length / self.data_length
        ) # Get the Y coordinate of the wick's high relatively to the price range
        self.candles.loc[mask, 'y_wick_low'] = self.grid_y_size[1] - round(
            (self.candles.loc[mask, 'low'] - self.data_min) * self.grid_y_length / self.data_length
        ) # Get the Y coordinate of the wick's low relatively to the price range

    def drawRectangle(self: object, x_start: int, y_start: int, x_end: int, y_end: int, color: Tuple[int, int, int]) -> None:
        """
        Draw a rectangle on the chart
        :param x_start: The X coordinate of the start of the rectangle
        :param y_start: The Y coordinate of the start of the rectangle
        :param x_end: The X coordinate of the end of the rectangle
        :param y_end: The Y coordinate of the end of the rectangle
        :param color: The color of the rectangle
        """
        rectangle = sdl2.SDL_Rect(
            int(x_start),
            int(y_start),
            int(x_end - x_start),
            int(y_end - y_start)
        )

        sdl2.SDL_SetRenderDrawColor(self.sdl_renderer, color[0], color[1], color[2], 255)
        sdl2.SDL_RenderFillRect(self.sdl_renderer, rectangle)

    def drawLine(self: object, x_start: int, x_end: int, y_start: int, y_end: int, color: Tuple[int, int, int]) -> None:
        """
        Draw a line on the chart
        :param x_start: The X coordinate of the start of the line
        :param x_end: The X coordinate of the end of the line
        :param y_start: The Y coordinate of the start of the line
        :param y_end: The Y coordinate of the end of the line
        :param color: The color of the line
        """
        sdl2.SDL_SetRenderDrawColor(self.sdl_renderer, color[0], color[1], color[2], 255)
        sdl2.SDL_RenderDrawLine(self.sdl_renderer, int(x_start), int(y_start), int(x_end), int(y_end))

    def drawCandles(self: object) -> None:
        """
        Draw the candles on the chart
        """
        sdl2.SDL_SetRenderDrawColor(self.sdl_renderer, *self.theme["Background"])
        sdl2.SDL_RenderClear(self.sdl_renderer)

        mask = self.candles['datetime'] != 0 # Filter the part of the DataFrame that contains candles

        for _, candle in self.candles[mask].iterrows():
            if candle["direction"] == "Bullish":
                self.drawRectangle(candle["x_start"], candle["y_body_start"], candle["x_end"], candle["y_body_end"], self.theme["Candle"]["Bullish"])
                self.drawLine(candle["x_center"], candle["x_center"], candle["y_wick_high"], candle["y_wick_low"], self.theme["Candle"]["Bullish"])
            else:
                self.drawRectangle(candle["x_start"], candle["y_body_start"], candle["x_end"], candle["y_body_end"], self.theme["Candle"]["Bearish"])
                self.drawLine(candle["x_center"], candle["x_center"], candle["y_wick_high"], candle["y_wick_low"], self.theme["Candle"]["Bearish"])

        sdl2.SDL_RenderPresent(self.sdl_renderer)

    def screenShot(self: object, filename=None) -> None:
        """
        Take a screenshot of the chart
        :param filename: The name of the file where the screenshot will be saved
        """
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
            ) # Create a surface to store the pixels
            
            if not surface:
                print(f"Error creating surface: {sdl2.SDL_GetError().decode()}")

                return

            if sdl2.SDL_RenderReadPixels(
                self.sdl_renderer,
                None,  # rect=None means entire renderer
                surface.contents.format.contents.format,
                surface.contents.pixels,
                surface.contents.pitch
            ) < 0: # if the pixels could not be read
                
                print(f"Error reading pixels: {sdl2.SDL_GetError().decode()}")

                sdl2.SDL_FreeSurface(surface)

                return

            pixels = cast(surface.contents.pixels, POINTER(c_ubyte)) # Get the pixels from the surface
            pixel_data = bytes(pixels[: self.size[0] * self.size[1] * 4]) # Get the pixel data
            
            image = Image.frombytes(
                'RGBA',
                self.size,
                pixel_data,
                'raw',
                'BGRA'  
            ) # Create an image from the pixel data

            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"

            image.save(filename)

            sdl2.SDL_FreeSurface(surface)

        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")

    async def quit(self: object) -> None:
        """
        Quit the SDL2 window
        """
        if self.window:
            self.window.close()  

        sdl2.ext.quit()

    def signal_quit(self: object) -> None:
        """
        Signal the window to quit the event loop.
        """
        self.running = False
        self.quit_event.set()
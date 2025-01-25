import asyncio
import sdl2
import sdl2.ext

class SDL2Window:
    def __init__(self, title="PySDL2 Window", size=(800, 600)):
        self.title = title
        self.size = size
        self.window = None
        self.running = False
        self.quit_event = asyncio.Event()  # Event to signal the window to quit

    async def init(self):
        """Initialize SDL2 and create a window."""
        sdl2.ext.init()

        self.window = sdl2.ext.Window(self.title, size=self.size)
        self.window.show()

        self.running = True

    async def handle_events(self):
        """Handle events within the window."""
        events = sdl2.ext.get_events()

        for event in events:
            if event.type == sdl2.SDL_QUIT:
                self.running = False

    async def run(self):
        """Run the event loop."""
        await self.init()
        
        while self.running:
            await self.handle_events()
            await asyncio.sleep(0.01)

        await self.quit()

    async def quit(self):
        """Cleanup, close the window, and quit SDL2."""
        if self.window:
            self.window.close()  

        sdl2.ext.quit()

    def signal_quit(self):
        """Signal the window to quit the event loop."""
        self.running = False
        self.quit_event.set()
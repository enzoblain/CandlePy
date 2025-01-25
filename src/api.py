# External imports
import asyncio
import sdl2
import sdl2.ext

# Application Programming Interface

async def api():
    sdl2.ext.init()
    window = sdl2.ext.Window("PySDL2 Window", size=(800, 600))
    window.show()
    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
        await asyncio.sleep(0.01)  # Yield control back to the event loop
    sdl2.ext.quit()
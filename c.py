import stdio
import SDL2.SDL


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

window: Pointer(SDL_Window) = None
renderer: Pointer(SDL_Renderer) = None
game_is_running: int = False


def main(argc: int, argv: list(str)) -> int:
    game_is_running = initialise_window()

    setup()

    while game_is_running:
        process_input()
        update()
        render()

    destroy_window

    return 0

def update():
    return

def render():
    return

def destroy_window():
    SDL_DestroyRenderer(renderer)
    SDL_DestroyWindow(window)
    SDL_Quit()


def setup():
    return


def process_input():
    event: SDL_Event = init_block(0)

    SDL_PollEvent(byref(event))

    match event.type:
        case SDL_QUIT:
            game_is_running = False
        case SDL_KEYDOWN:
            if event.key.keysym.sym == SDLK_ESCAPE:
                game_is_running = False


def initialise_window() -> int:
    if SDL_Init(SDL_INIT_EVERYTHING) != 0:
        fprintf(stderr, "Error: initialising SDL.\n")
        return False

    window = SDL_Create_Window(
            None,
            SDL_WINDOWPOS_CENTERERED,
            SDL_WINDOWPOS_CENTERERED,
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            SDL_WINDOW_BORDERLESS)

    if not window:
        fprintf(stderr, "Error creating SDL Window.\n")
        return False

    renderer = SDL_CreateRenderer(window, -1, 0)

    if not renderer:
        fprintf(stderr, "Error creating SDL Renderer.\n")
        return False

    return True



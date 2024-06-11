"""flappybird - Flappy bird, but every sprite is its own window."""

from __future__ import annotations

import os
from time import sleep
from typing import Iterator, TypeVar
import pygame
from pygame._sdl2 import Window, Texture, Renderer


ASSERTS_DIR = os.path.join(os.path.dirname(__file__), "assets")
WINDOW_SIZE = pygame.display.set_mode().get_size()
SPRITE_SCALE = 0.2


def load_image(filename: str) -> pygame.Surface:
    return pygame.image.load(os.path.join(ASSERTS_DIR, filename))


def vw(percent: int) -> float:
    """Scale a percent of window width to the pixel position."""
    width, _ = WINDOW_SIZE
    return width * percent / 100


def vh(percent: int) -> float:
    """Scale a percent of window height to the pixel position."""
    _, height = WINDOW_SIZE
    return height * percent / 100


def create_bird() -> Window:
    image = load_image("bird.png")

    # Make the sprite sizes constant with the window height
    width = vh(image.get_width() * SPRITE_SCALE)
    height = vh(image.get_height() * SPRITE_SCALE)

    window = Window("bird", size=(width, height), always_on_top=True)
    renderer = Renderer(window)
    image_texture = Texture.from_surface(renderer, image)

    renderer.clear()
    image_texture.draw()
    renderer.present()

    return window


def create_pipes() -> list[Window]:
    top_pipe = load_image("top_pipe.png")
    bottom_pipe = load_image("bottom_pipe.png")

    # Make the sprite sizes constant with the window height
    width = vh(top_pipe.get_width() * SPRITE_SCALE)
    top_pipe_height = vh(20)
    bottom_pipe_height = vh(40)
    top_pipe_position = (vw(90), 0)
    bottom_pipe_position = (vw(90), vh(60))

    top_pipe_window = Window(
        "top pipe",
        size=(width, top_pipe_height),
        position=top_pipe_position,
        always_on_top=True,
    )
    renderer = Renderer(top_pipe_window)
    image_texture = Texture.from_surface(renderer, top_pipe)

    renderer.clear()
    image_texture.draw()
    renderer.present()

    bottom_pipe_window = Window(
        "bottom pipe",
        size=(width, bottom_pipe_height),
        position=bottom_pipe_position,
        always_on_top=True,
    )
    renderer = Renderer(bottom_pipe_window)
    image_texture = Texture.from_surface(renderer, bottom_pipe)

    renderer.clear()
    image_texture.draw()
    renderer.present()

    return [top_pipe_window, bottom_pipe_window]


T = TypeVar("T")


def reversed_enumerate(items: list[T]) -> Iterator[tuple[int, T]]:
    index = len(items) - 1
    for item in reversed(items):
        yield index, item
        index -= 1


def main() -> None:
    bird = create_bird()
    pipes = create_pipes()

    _, y = bird.position
    bird.position = (vw(7), y)
    bird.focus()

    bird_speed = 0
    while True:
        # move pipes towards bird
        for pipe_index, pipe in reversed_enumerate(pipes):
            x, y = pipe.position
            x -= vw(0.4)
            # delete the pipe if it reaches edge of screen
            if x <= 0:
                pipe.destroy()
                del pipes[pipe_index]

            pipe.position = x, y

        # gravity
        bird_speed += vh(0.15)
        x, y = bird.position
        y += bird_speed
        # Exit if you hit the bottom
        if y >= vh(100):
            break

        bird.position = x, y

        # handle jumps
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird_speed = vh(-2.5)

        # smooth 30 fps
        sleep(0.03)

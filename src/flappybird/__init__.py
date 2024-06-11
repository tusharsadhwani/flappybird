"""flappybird - Flappy bird, but every sprite is its own window."""

from __future__ import annotations

import os
from time import sleep
import pygame
from pygame._sdl2 import Window, Texture, Renderer


ASSERTS_DIR = os.path.join(os.path.dirname(__file__), "assets")

WINDOW_SIZE = pygame.display.set_mode().get_size()


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


def create_sprite(filename: str) -> Window:
    image = load_image(filename)

    # Make the sprite sizes constant with the window height
    scale = 0.2
    width = vh(image.get_width() * scale)
    height = vh(image.get_height() * scale)

    window = Window(filename, size=(width, height), always_on_top=True)
    renderer = Renderer(window)
    image_texture = Texture.from_surface(renderer, image)

    renderer.clear()
    image_texture.draw()
    renderer.present()

    return window


def main() -> None:
    bird = create_sprite("bird.png")
    pipe = create_sprite("pipe.png")

    _, y = bird.position
    bird.position = (vw(7), y)
    bird.focus()

    bird_speed = 0
    while True:
        # gravity
        bird_speed += vh(0.15)

        x, y = bird.position
        bird.position = (x, y + bird_speed)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_speed = vh(-2.5)

        _, y = bird.position
        if y >= vh(100):
            break

        # smooth 30 fps
        sleep(0.03)

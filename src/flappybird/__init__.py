"""flappybird - Flappy bird, but every sprite is its own window."""

from __future__ import annotations

import os
import pygame
from pygame._sdl2 import Window, Texture, Renderer


ASSERTS_DIR = os.path.join(os.path.dirname(__file__), "assets")


def load_image(filename: str) -> pygame.Surface:
    return pygame.image.load(os.path.join(ASSERTS_DIR, filename))


def create_sprite(filename: str, *, scale: float = 1.0) -> Window:
    image = load_image(filename)
    width = image.get_width()
    height = image.get_height()

    window = Window(filename, size=(width * scale, height * scale), always_on_top=True)
    renderer = Renderer(window)
    image_texture = Texture.from_surface(renderer, image)

    renderer.clear()
    image_texture.draw()
    renderer.present()

    return window


def jump(bird: Window) -> None:
    x, y = bird.position
    bird.position = (x, max(0, y - 20))


def main() -> None:
    bird = create_sprite("bird.png", scale=2)
    pipe = create_sprite("pipe.png", scale=2)

    _, y = bird.position
    bird.position = (100, y)
    bird.focus()

    running = True
    while running:
        for event in pygame.event.get():
            # if event.type == pygame.QUIT:
            #     running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    jump(bird)
                    print(bird.position)

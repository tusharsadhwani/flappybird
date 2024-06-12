"""flappybird - Flappy bird, but every sprite is its own window."""

from __future__ import annotations

import os
import random
from time import sleep
from typing import Iterator, TypeVar
import pygame
from pygame._sdl2 import Window, Texture, Renderer


ASSERTS_DIR = os.path.join(os.path.dirname(__file__), "assets")
WINDOW_SIZE = pygame.display.set_mode(flags=pygame.HIDDEN).get_size()
SPRITE_SCALE = 0.2
# frames after which to spawn a new pipe
PIPE_SPAWN_DISTANCE = 100


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


BIRD_TERMINAL_VELOCITY = vh(2.5)
PIPE_GAP = vh(40)
PIPE_SPAWN_POSITION = vw(90)


def create_bird() -> Window:
    image = load_image("bird.png")

    # Make the sprite sizes constant with the window height
    width = vh(image.get_width() * SPRITE_SCALE)
    height = vh(image.get_height() * SPRITE_SCALE)

    bird = Window(
        "bird",
        size=(width, height),
        position=(vw(10), vh(50)),
        always_on_top=True,
    )
    renderer = Renderer(bird)
    image_texture = Texture.from_surface(renderer, image)

    renderer.clear()
    image_texture.draw()
    renderer.present()

    return bird


def create_pipes() -> list[Window]:
    top_pipe = load_image("top_pipe.png")
    bottom_pipe = load_image("bottom_pipe.png")

    # Make the sprite sizes constant with the window height
    width = vh(top_pipe.get_width() * SPRITE_SCALE)
    top_pipe_height = vh(random.randint(10, 30))
    bottom_pipe_height = vh(100) - PIPE_GAP - top_pipe_height

    top_pipe_position = (PIPE_SPAWN_POSITION, 0)
    bottom_pipe_position = (PIPE_SPAWN_POSITION, top_pipe_height + PIPE_GAP)

    # pipe images must be cropped to the size of the window
    image_width, image_height = top_pipe.get_size()
    cropped_top_pipe_height = top_pipe_height * (image_width / width)
    assert cropped_top_pipe_height < image_height
    image_width, image_height = bottom_pipe.get_size()
    cropped_bottom_pipe_height = bottom_pipe_height * (image_width / width)
    assert cropped_bottom_pipe_height < image_height

    # crop the top pipe image to that height from the bottom
    cropped_top_pipe = pygame.Surface((image_width, cropped_top_pipe_height))
    cropped_top_pipe.blit(
        top_pipe,
        (0, 0),
        (0, image_height - cropped_top_pipe_height, image_width, image_height),
    )
    cropped_bottom_pipe = pygame.Surface((image_width, cropped_bottom_pipe_height))
    cropped_bottom_pipe.blit(
        bottom_pipe,
        (0, 0),
        (0, 0, image_width, cropped_bottom_pipe_height),
    )

    top_pipe_window = Window(
        "top pipe",
        size=(width, top_pipe_height),
        position=top_pipe_position,
        always_on_top=True,
    )
    renderer = Renderer(top_pipe_window)
    image_texture = Texture.from_surface(renderer, cropped_top_pipe)

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
    image_texture = Texture.from_surface(renderer, cropped_bottom_pipe)

    renderer.clear()
    image_texture.draw()
    renderer.present()

    top_bound = top_pipe_window.position[1]
    return [top_pipe_window, bottom_pipe_window], top_bound


T = TypeVar("T")


def reversed_enumerate(items: list[T]) -> Iterator[tuple[int, T]]:
    index = len(items) - 1
    for item in reversed(items):
        yield index, item
        index -= 1


def _is_in_bounds(x: int, y: int, x1: int, y1: int, x2: int, y2: int) -> bool:
    print(f"{x1} <= {x} <= {x2} and {y1} <= {y} <= {y2}")
    return x1 <= x <= x2 and y1 <= y <= y2


def _colliding(item1: Window, item2: Window) -> bool:
    """Checks if any corner of item1 is inside item2's bounding box."""
    (x1, y1), (w1, h1) = item1.position, item1.size
    (x2, y2), (w2, h2) = item2.position, item2.size

    item2_bounding_box = x2, y2, x2 + w2, y2 + h2
    print("-------------------")
    return (
        # top left corner
        _is_in_bounds(x1, y1, *item2_bounding_box)
        # top right edge
        or _is_in_bounds(x1 + w1, y1, *item2_bounding_box)
        # bottom left corner
        or _is_in_bounds(x1, y1 + h1, *item2_bounding_box)
        # bottom right edge
        or _is_in_bounds(x1 + w1, y1 + h1, *item2_bounding_box)
    )


def colliding(item1: Window, item2: Window) -> bool:
    """Detects if item1 is colliding with item2"""
    return _colliding(item1, item2) or _colliding(item2, item1)


def main() -> None:
    bird = create_bird()
    pipes, top_bound = create_pipes()

    bird.focus()

    frame_count = 0
    bird_speed = 0
    dead = False
    while not dead:
        # collision detection
        print("\n")
        for pipe in pipes:
            if colliding(bird, pipe):
                dead = True
                break

        # after every PIPE_SPAWN_DISTANCE frames, spawn new pipes
        frame_count += 1
        frame_count %= PIPE_SPAWN_DISTANCE
        if frame_count == 0:
            pipes, _ = create_pipes()
            pipes.extend(pipes)

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
        bird_speed = min(bird_speed + vh(0.15), BIRD_TERMINAL_VELOCITY)
        x, y = bird.position
        y += bird_speed
        # ensure we don't go below top_bound when bird_speed is negative
        if y < top_bound:
            y = top_bound
        # Exit if you hit the bottom
        elif y >= vh(100):
            dead = True

        bird.position = x, y

        # handle jumps
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird_speed = -BIRD_TERMINAL_VELOCITY

        # smooth 30 fps
        sleep(0.03)

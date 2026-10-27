"""Loop do jogo, igual para as duas versões.

O loop só depende de `forest.trees` (lista ordenada por y) e de `tree.draw(screen, camera)`,
então trocar a floresta sem Flyweight pela com Flyweight não muda nada aqui.
"""

from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Protocol

import pygame

from .camera import Camera
from .config import BORDER_COLOR, FPS, GRASS_COLOR, REPORT_INTERVAL, SCREEN_SIZE, WORLD_SIZE
from .metrics import Reporter
from .player import Player


class DrawableTree(Protocol):
    x: int
    y: int

    def draw(self, screen: pygame.Surface, camera: Camera) -> None: ...


class Forest(Protocol):
    trees: Sequence[DrawableTree]


def open_window(title: str) -> pygame.Surface:
    pygame.init()
    pygame.display.set_caption(title)
    return pygame.display.set_mode(SCREEN_SIZE)


def run(screen: pygame.Surface, forest: Forest, seconds: float | None = None) -> None:
    """Roda até fechar a janela, apertar ESC ou passar `seconds` segundos."""
    clock = pygame.time.Clock()
    camera = Camera()
    player = Player(WORLD_SIZE[0] / 2, WORLD_SIZE[1] / 2)
    reporter = Reporter(REPORT_INTERVAL)
    world_border = pygame.Rect((0, 0), WORLD_SIZE)
    started = time.perf_counter()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        if seconds is not None and time.perf_counter() - started >= seconds:
            running = False

        player.update(dt)
        camera.follow(player.pos)

        screen.fill(GRASS_COLOR)
        pygame.draw.rect(screen, BORDER_COLOR, world_border.move(-camera.rect.x, -camera.rect.y), 8)

        # Árvores em ordem de y: as de trás primeiro. O jogador entra no meio,
        # na posição certa, para passar por trás/na frente das árvores.
        visible = camera.visible(forest.trees)
        player_drawn = False
        for tree in visible:
            if not player_drawn and tree.y > player.pos.y:
                player.draw(screen, camera)
                player_drawn = True
            tree.draw(screen, camera)
        if not player_drawn:
            player.draw(screen, camera)

        pygame.display.flip()
        reporter.update(clock, len(visible))

    reporter.print_summary()
    pygame.quit()

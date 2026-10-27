"""Jogador: anda nas 4 direções (e diagonais), sem gravidade."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from .config import PLAYER_COLOR, PLAYER_SIZE, PLAYER_SPEED, WORLD_SIZE

if TYPE_CHECKING:
    from .camera import Camera


class Player:
    def __init__(self, x: float, y: float) -> None:
        # A posição é o "pé" do jogador, igual à base do tronco das árvores,
        # para comparar profundidade (quem está mais embaixo é desenhado na frente).
        self.pos = pygame.Vector2(x, y)

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT]),
            (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP]),
        )
        if direction.length_squared() > 0:
            # Normaliza para a diagonal não ser mais rápida.
            self.pos += direction.normalize() * PLAYER_SPEED * dt
        half = PLAYER_SIZE / 2
        self.pos.x = min(max(self.pos.x, half), WORLD_SIZE[0] - half)
        self.pos.y = min(max(self.pos.y, PLAYER_SIZE), WORLD_SIZE[1])

    def draw(self, screen: pygame.Surface, camera: Camera) -> None:
        rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        rect.midbottom = camera.apply(self.pos.x, self.pos.y)
        pygame.draw.rect(screen, PLAYER_COLOR, rect, border_radius=6)
        pygame.draw.rect(screen, (60, 20, 20), rect, 2, border_radius=6)

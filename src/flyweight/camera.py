"""Câmera que segue o jogador e decide quais árvores aparecem na tela."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections.abc import Sequence
from typing import Protocol

import pygame

from .config import SCREEN_SIZE, WORLD_SIZE
from .sprites import MAX_TREE_HEIGHT, MAX_TREE_WIDTH


class Positioned(Protocol):
    x: int
    y: int


class Camera:
    def __init__(self) -> None:
        self.rect = pygame.Rect((0, 0), SCREEN_SIZE)

    def follow(self, target: pygame.Vector2) -> None:
        """Centraliza no alvo sem mostrar nada fora do mundo."""
        self.rect.center = (round(target.x), round(target.y))
        self.rect.clamp_ip(pygame.Rect((0, 0), WORLD_SIZE))

    def apply(self, x: float, y: float) -> tuple[float, float]:
        """Converte coordenadas do mundo para coordenadas da tela."""
        return x - self.rect.x, y - self.rect.y

    def visible[T: Positioned](self, items: Sequence[T]) -> list[T]:
        """Itens que aparecem na tela. `items` precisa estar ordenado por y.

        Como a lista está ordenada, uma busca binária acha a faixa de y visível
        e só essa faixa é filtrada por x. A margem garante que árvores com a base
        logo abaixo da tela (mas a copa dentro dela) também sejam desenhadas.
        """
        lo = bisect_left(items, self.rect.top, key=lambda item: item.y)
        hi = bisect_right(items, self.rect.bottom + MAX_TREE_HEIGHT, key=lambda item: item.y)
        left = self.rect.left - MAX_TREE_WIDTH
        right = self.rect.right + MAX_TREE_WIDTH
        return [item for item in items[lo:hi] if left <= item.x <= right]

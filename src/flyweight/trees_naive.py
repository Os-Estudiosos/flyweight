"""Floresta SEM o padrão Flyweight.

Cada árvore guarda tudo o que precisa para ser desenhada: posição, nome da espécie,
cores e o próprio sprite. Com N árvores e 4 espécies existem N sprites, embora só
4 sejam realmente diferentes. Cada sprite é uma Surface RGBA de ~25-43 KB, então
a memória cresce linearmente com o número de árvores.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import pygame

from .sprites import Color, draw_tree_sprite, random_plantings

if TYPE_CHECKING:
    from .camera import Camera


class Tree:
    """Árvore "gorda": estado único (x, y) e estado repetido (resto) juntos."""

    __slots__ = ("x", "y", "name", "crown_color", "trunk_color", "sprite")

    def __init__(self, x: int, y: int, name: str, crown_color: Color, trunk_color: Color, width: int, height: int, shape: str) -> None:
        self.x = x
        self.y = y
        self.name = name
        self.crown_color = crown_color
        self.trunk_color = trunk_color
        # Cada árvore desenha (e mantém na memória) a sua própria cópia do sprite.
        self.sprite = draw_tree_sprite(crown_color, trunk_color, width, height, shape)

    def draw(self, screen: pygame.Surface, camera: Camera) -> None:
        sx, sy = camera.apply(self.x, self.y)
        screen.blit(self.sprite, (sx - self.sprite.get_width() // 2, sy - self.sprite.get_height()))


class Forest:
    def __init__(self) -> None:
        self.trees: list[Tree] = []

    def plant_tree(self, x: int, y: int, name: str, crown_color: Color, trunk_color: Color, width: int, height: int, shape: str) -> None:
        self.trees.append(Tree(x, y, name, crown_color, trunk_color, width, height, shape))

    def sprites(self) -> Iterator[pygame.Surface]:
        """Sprite usado por cada árvore (para as métricas)."""
        return (tree.sprite for tree in self.trees)


def build_forest(count: int, seed: int, world_size: tuple[int, int]) -> Forest:
    forest = Forest()
    for x, y, kind in random_plantings(count, seed, world_size):
        forest.plant_tree(x, y, kind.name, kind.crown_color, kind.trunk_color, kind.width, kind.height, kind.shape)
    # Ordenada por y: permite desenhar de trás para frente e buscar as visíveis.
    forest.trees.sort(key=lambda tree: tree.y)
    return forest

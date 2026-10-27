"""Espécies de árvore e o desenho do sprite de cada uma.

As duas versões do jogo usam a mesma função `draw_tree_sprite`. A única diferença
entre elas é QUANTAS vezes ela é chamada: uma vez por árvore (sem Flyweight) ou
uma vez por espécie (com Flyweight).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

Color = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class TreeKind:
    """Dados de uma espécie, como viriam de um arquivo de configuração."""

    name: str
    crown_color: Color
    trunk_color: Color
    width: int
    height: int
    shape: str  # "pine" (triângulos) ou "round" (círculos)


TREE_KINDS: tuple[TreeKind, ...] = (
    TreeKind("Pinheiro", (34, 100, 52), (92, 60, 34), 72, 128, "pine"),
    TreeKind("Carvalho", (48, 130, 46), (110, 72, 40), 96, 112, "round"),
    TreeKind("Bétula", (140, 190, 80), (225, 225, 215), 64, 112, "round"),
    TreeKind("Cerejeira", (235, 150, 185), (100, 60, 50), 88, 104, "round"),
)

# Maior sprite possível: usado pela câmera para não cortar árvores na borda da tela.
MAX_TREE_WIDTH = max(k.width for k in TREE_KINDS)
MAX_TREE_HEIGHT = max(k.height for k in TREE_KINDS)


def _darker(color: Color, amount: int = 30) -> Color:
    r, g, b = color
    return (max(r - amount, 0), max(g - amount, 0), max(b - amount, 0))


def draw_tree_sprite(crown_color: Color, trunk_color: Color, width: int, height: int, shape: str) -> pygame.Surface:
    """Cria uma Surface nova (RGBA, width x height x 4 bytes) com a árvore desenhada."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    trunk_w = max(width // 6, 6)
    trunk_h = height // 3
    trunk = pygame.Rect(0, 0, trunk_w, trunk_h)
    trunk.midbottom = (width // 2, height)
    pygame.draw.rect(surface, trunk_color, trunk)
    pygame.draw.rect(surface, _darker(trunk_color), trunk, 1)

    crown_bottom = height - trunk_h + 8
    if shape == "pine":
        layers = 3
        layer_h = crown_bottom // layers + 8
        for i in range(layers):
            bottom = crown_bottom - i * (layer_h - 14)
            half = width // 2 - i * 8
            points = [(width // 2 - half, bottom), (width // 2 + half, bottom), (width // 2, bottom - layer_h)]
            pygame.draw.polygon(surface, crown_color, points)
            pygame.draw.polygon(surface, _darker(crown_color), points, 2)
    else:
        r = width // 4
        cy = crown_bottom - r - 4
        for dx, dy in ((-r, 0), (r, 0), (0, -r), (0, r // 2)):
            pygame.draw.circle(surface, _darker(crown_color), (width // 2 + dx, cy + dy), r + 2)
        for dx, dy in ((-r, 0), (r, 0), (0, -r), (0, r // 2)):
            pygame.draw.circle(surface, crown_color, (width // 2 + dx, cy + dy), r)
    return surface


def random_plantings(count: int, seed: int, world_size: tuple[int, int]) -> list[tuple[int, int, TreeKind]]:
    """Posições e espécies aleatórias (mas reprodutíveis) das árvores."""
    rng = random.Random(seed)
    w, h = world_size
    return [
        (rng.randint(MAX_TREE_WIDTH // 2, w - MAX_TREE_WIDTH // 2), rng.randint(MAX_TREE_HEIGHT, h), rng.choice(TREE_KINDS))
        for _ in range(count)
    ]

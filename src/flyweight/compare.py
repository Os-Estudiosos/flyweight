"""Compara as duas versões da floresta para mostrar que o comportamento foi preservado.

    uv run comparar-versoes [--arvores N]

1. As duas versões plantam as mesmas árvores (posição e espécie), na mesma ordem.
2. As duas desenham a mesma imagem, pixel a pixel, com a câmera em 9 pontos do mundo.
Não abre janela.
"""

from __future__ import annotations

import argparse

import pygame

from . import trees_flyweight, trees_naive
from .camera import Camera
from .config import DEFAULT_TREES, GRASS_COLOR, SCREEN_SIZE, SEED, WORLD_SIZE


def render(forest: trees_naive.Forest | trees_flyweight.Forest, center: tuple[int, int]) -> tuple[bytes, int]:
    """Desenha as árvores visíveis com a câmera centrada em `center`, como o loop do jogo faz."""
    screen = pygame.Surface(SCREEN_SIZE)
    camera = Camera()
    camera.follow(pygame.Vector2(center))
    screen.fill(GRASS_COLOR)
    visible = camera.visible(forest.trees)
    for tree in visible:
        tree.draw(screen, camera)
    return pygame.image.tobytes(screen, "RGB"), len(visible)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara as florestas SEM e COM Flyweight")
    parser.add_argument("--arvores", type=int, default=DEFAULT_TREES, help=f"quantidade de árvores (padrão: {DEFAULT_TREES})")
    args = parser.parse_args()

    naive = trees_naive.build_forest(args.arvores, SEED, WORLD_SIZE)
    flyweight = trees_flyweight.build_forest(args.arvores, SEED, WORLD_SIZE)

    same_trees = sum(
        (a.x, a.y, a.name, a.crown_color, a.trunk_color) == (b.x, b.y, b.type.name, b.type.crown_color, b.type.trunk_color)
        for a, b in zip(naive.trees, flyweight.trees, strict=True)
    )

    w, h = WORLD_SIZE
    centers = [(x, y) for y in (h // 6, h // 2, 5 * h // 6) for x in (w // 6, w // 2, 5 * w // 6)]
    same_frames = drawn = 0
    for center in centers:
        image_naive, visible = render(naive, center)
        image_flyweight, _ = render(flyweight, center)
        same_frames += image_naive == image_flyweight
        drawn += visible

    def num(n: int) -> str:
        return f"{n:,}".replace(",", ".")

    print(f"=== Comparando as duas versões ({num(len(naive.trees))} árvores, seed {SEED}) ===")
    print(f"Mesmas árvores (posição e espécie), na mesma ordem: {num(same_trees)} de {num(len(naive.trees))}")
    print(f"Mesma imagem, pixel a pixel, em {len(centers)} posições da câmera: {same_frames} de {len(centers)}"
          f" ({num(drawn)} árvores desenhadas)")
    ok = same_trees == len(naive.trees) and same_frames == len(centers)
    print("Resultado: comportamento preservado" if ok else "Resultado: as versões DIFEREM")
    raise SystemExit(0 if ok else 1)

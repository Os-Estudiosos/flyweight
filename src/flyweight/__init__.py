"""Jogo da floresta em duas versões: sem e com o padrão Flyweight.

    uv run jogo-sem-flyweight [--arvores N] [--segundos S]
    uv run jogo-com-flyweight [--arvores N] [--segundos S]
"""

from __future__ import annotations

import argparse
import time

from . import game, trees_flyweight, trees_naive
from .config import DEFAULT_TREES, SEED, WORLD_SIZE
from .metrics import print_forest_report, rss_mb


def _parse_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--arvores", type=int, default=DEFAULT_TREES, help=f"quantidade de árvores (padrão: {DEFAULT_TREES})")
    parser.add_argument("--segundos", type=float, default=None, help="fecha o jogo sozinho depois de S segundos (útil para medir)")
    return parser.parse_args()


def _start(title: str, build_forest) -> None:
    args = _parse_args(title)
    screen = game.open_window(title)

    rss_before = rss_mb()
    started = time.perf_counter()
    forest = build_forest(args.arvores, SEED, WORLD_SIZE)
    elapsed = time.perf_counter() - started
    print_forest_report(title, forest.sprites(), elapsed, rss_before)

    game.run(screen, forest, args.segundos)


def main_naive() -> None:
    _start("Floresta SEM Flyweight", trees_naive.build_forest)


def main_flyweight() -> None:
    _start("Floresta COM Flyweight", trees_flyweight.build_forest)

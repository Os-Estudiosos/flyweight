"""Métricas impressas no terminal (RAM, CPU, FPS e sprites em memória).

O RSS (memória residente do processo) vem do psutil. O tracemalloc não serviria
aqui: os pixels das Surfaces são alocados pelo SDL, em C, fora do alocador do Python.
"""

from __future__ import annotations

import sys
import time
from collections.abc import Iterable

import psutil
import pygame

_process = psutil.Process()


def rss_mb() -> float:
    return _process.memory_info().rss / 1024**2


def peak_rss_mb() -> float | None:
    """Pico de RSS do processo (só em sistemas Unix)."""
    try:
        import resource
    except ImportError:
        return None
    # No Linux ru_maxrss vem em KB; no macOS, em bytes.
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak / 1024**2 if sys.platform == "darwin" else peak / 1024


def print_forest_report(title: str, sprites: Iterable[pygame.Surface], seconds: float, rss_before: float) -> None:
    trees = 0
    unique: dict[int, pygame.Surface] = {}
    for sprite in sprites:
        trees += 1
        unique[id(sprite)] = sprite
    sprite_bytes = sum(s.get_width() * s.get_height() * s.get_bytesize() for s in unique.values())
    rss_after = rss_mb()

    print(f"=== {title} ===")
    print(f"Árvores                      {trees:>12,}".replace(",", "."))
    print(f"Sprites (Surfaces) distintos {len(unique):>12,}".replace(",", "."))
    print(f"Memória dos sprites          {sprite_bytes / 1024**2:>9.1f} MB")
    print(f"Tempo para criar a floresta  {seconds * 1000:>9.0f} ms")
    print(f"RSS antes da floresta        {rss_before:>9.1f} MB")
    print(f"RSS depois da floresta       {rss_after:>9.1f} MB  (+{rss_after - rss_before:.1f} MB)")
    print(flush=True)


class Reporter:
    """Imprime FPS, RAM e CPU a cada `interval` segundos enquanto o jogo roda."""

    def __init__(self, interval: float) -> None:
        self.interval = interval
        self._last = time.perf_counter()
        self._cpu_samples: list[float] = []
        _process.cpu_percent()  # a primeira leitura só zera o contador

    def update(self, clock: pygame.time.Clock, visible_trees: int) -> None:
        now = time.perf_counter()
        if now - self._last < self.interval:
            return
        self._last = now
        cpu = _process.cpu_percent()
        self._cpu_samples.append(cpu)
        print(f"FPS {clock.get_fps():5.1f} | RAM (RSS) {rss_mb():7.1f} MB | CPU {cpu:5.1f}% | árvores na tela {visible_trees}", flush=True)

    def print_summary(self) -> None:
        print()
        if self._cpu_samples:
            print(f"CPU média durante o jogo     {sum(self._cpu_samples) / len(self._cpu_samples):>9.1f} %")
        peak = peak_rss_mb()
        if peak is not None:
            print(f"Pico de RAM (RSS)            {peak:>9.1f} MB")

"""Floresta COM o padrão Flyweight.

Estrutura igual ao exemplo de https://refactoring.guru/design-patterns/flyweight:
separar o estado
  - intrínseco -> TreeType (nome, cores e sprite: compartilhado e imutável)
  - extrínseco -> Tree     (x, y: único de cada árvore)
e usar uma fábrica (TreeFactory) que garante um único TreeType por espécie.

Com N árvores e 4 espécies existem só 4 sprites; cada Tree guarda duas coordenadas
e uma referência, então a memória por árvore fica em poucas dezenas de bytes.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pygame

from .sprites import Color, draw_tree_sprite, random_plantings

if TYPE_CHECKING:
    from .camera import Camera


@dataclass(frozen=True, slots=True)
class TreeType:
    """Flyweight: estado intrínseco de uma espécie.

    frozen=True -> imutável: o mesmo objeto é usado por milhares de árvores
    slots=True  -> sem __dict__ por instância
    """

    name: str
    crown_color: Color
    trunk_color: Color
    width: int
    height: int
    shape: str
    # O sprite é igual para todas as árvores da espécie: desenhado uma única vez.
    sprite: pygame.Surface = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        # Única escrita permitida: durante a construção do objeto.
        object.__setattr__(self, "sprite", draw_tree_sprite(self.crown_color, self.trunk_color, self.width, self.height, self.shape))

    def draw(self, screen: pygame.Surface, x: float, y: float) -> None:
        """O estado extrínseco (posição na tela) chega por parâmetro; o flyweight não o armazena."""
        screen.blit(self.sprite, (x - self.width // 2, y - self.height))


class TreeFactory:
    """Fábrica de flyweights: devolve o TreeType existente ou cria um novo.

    A chave é o próprio estado intrínseco, então duas espécies com os mesmos dados
    viram o mesmo objeto.
    """

    def __init__(self) -> None:
        self._pool: dict[tuple, TreeType] = {}

    def get_tree_type(self, name: str, crown_color: Color, trunk_color: Color, width: int, height: int, shape: str) -> TreeType:
        key = (name, crown_color, trunk_color, width, height, shape)
        tree_type = self._pool.get(key)
        if tree_type is None:
            tree_type = TreeType(*key)
            self._pool[key] = tree_type
        return tree_type

    def __len__(self) -> int:
        return len(self._pool)


class Tree:
    """Contexto: estado extrínseco (único de cada árvore) + referência ao flyweight."""

    __slots__ = ("x", "y", "type")

    def __init__(self, x: int, y: int, type: TreeType) -> None:
        self.x = x
        self.y = y
        self.type = type

    def draw(self, screen: pygame.Surface, camera: Camera) -> None:
        self.type.draw(screen, *camera.apply(self.x, self.y))


class Forest:
    """Cliente: planta árvores pedindo o TreeType à fábrica."""

    def __init__(self) -> None:
        self.factory = TreeFactory()
        self.trees: list[Tree] = []

    def plant_tree(self, x: int, y: int, name: str, crown_color: Color, trunk_color: Color, width: int, height: int, shape: str) -> None:
        tree_type = self.factory.get_tree_type(name, crown_color, trunk_color, width, height, shape)
        self.trees.append(Tree(x, y, tree_type))

    def sprites(self) -> Iterator[pygame.Surface]:
        """Sprite usado por cada árvore (para as métricas)."""
        return (tree.type.sprite for tree in self.trees)


def build_forest(count: int, seed: int, world_size: tuple[int, int]) -> Forest:
    forest = Forest()
    for x, y, kind in random_plantings(count, seed, world_size):
        forest.plant_tree(x, y, kind.name, kind.crown_color, kind.trunk_color, kind.width, kind.height, kind.shape)
    # Ordenada por y: permite desenhar de trás para frente e buscar as visíveis.
    forest.trees.sort(key=lambda tree: tree.y)
    return forest

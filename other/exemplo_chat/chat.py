"""Histórico de chat com o padrão Flyweight.

Problema: um canal tem dezenas de milhares de mensagens, mas só algumas dezenas
de autores. A API devolve cada mensagem com os dados do autor embutidos
(formato desnormalizado, comum em REST/GraphQL), então a abordagem ingênua
guarda em CADA mensagem uma cópia do nome, avatar, cor e cargo do autor.

Solução: separar o estado
  - intrínseco -> Author  (dados do autor: compartilhado e imutável)
  - extrínseco -> Message (texto e horário: únicos de cada mensagem)
e usar uma fábrica (AuthorFactory) que garante um único Author por perfil.

Requer Python 3.11+ (dataclass com weakref_slot).
"""

from __future__ import annotations

import html
import weakref
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# Formato de cada item devolvido pela API:
# {"id": 1, "body": "...", "sent_at": "2026-10-10T14:03:00+00:00",
#  "user": {"id": 7, "name": "...", "avatar_url": "...", "color": "#c0392b", "role": "admin"}}
RawMessage = Mapping[str, Any]


@dataclass(frozen=True, slots=True, weakref_slot=True)
class Author:
    """Flyweight: estado intrínseco de um autor.

    frozen=True        -> imutável: o mesmo objeto é usado por milhares de mensagens
    slots=True         -> sem __dict__ por instância
    weakref_slot=True  -> permite guardar o objeto num pool de referências fracas
    """

    id: int
    name: str
    avatar_url: str
    color: str
    role: str
    # Trecho de HTML igual em todas as mensagens do autor: calculado uma única vez.
    header_html: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        badge = f' <span class="badge">{html.escape(self.role)}</span>' if self.role != "member" else ""
        # Única escrita permitida: durante a construção do objeto.
        object.__setattr__(
            self,
            "header_html",
            f'<img class="avatar" src="{html.escape(self.avatar_url)}" alt="" width="32" height="32">'
            f'<strong style="color:{html.escape(self.color)}">{html.escape(self.name)}</strong>{badge}',
        )

    def render(self, body: str, sent_at: datetime) -> str:
        """O estado extrínseco chega por parâmetro; o flyweight não o armazena."""
        return (
            f'<li class="msg">{self.header_html}'
            f'<time datetime="{sent_at.isoformat()}">{sent_at:%d/%m %H:%M}</time>'
            f"<p>{html.escape(body)}</p></li>"
        )


class AuthorFactory:
    """Fábrica de flyweights: devolve o Author existente ou cria um novo.

    A chave é o próprio estado intrínseco. Se o usuário trocar de nome ou de
    avatar, a chave muda e um novo Author é criado; as mensagens antigas
    continuam apontando para o objeto antigo, que nunca é modificado.

    O pool é um WeakValueDictionary: quando nenhuma mensagem referencia mais
    um Author (ex.: o histórico foi descartado), ele sai do pool sozinho, o que
    evita vazamento de memória em processos de longa duração.
    """

    def __init__(self) -> None:
        self._pool: weakref.WeakValueDictionary[tuple, Author] = weakref.WeakValueDictionary()
        self.created = 0

    def get(self, user: Mapping[str, Any]) -> Author:
        key = (user["id"], user["name"], user["avatar_url"], user["color"], user["role"])
        author = self._pool.get(key)
        if author is None:
            author = Author(*key)
            self._pool[key] = author
            self.created += 1
        return author

    def __len__(self) -> int:
        return len(self._pool)


class Message:
    """Contexto: estado extrínseco (único de cada mensagem) + referência ao flyweight."""

    __slots__ = ("id", "author", "body", "sent_at")

    def __init__(self, id: int, author: Author, body: str, sent_at: datetime) -> None:
        self.id = id
        self.author = author
        self.body = body
        self.sent_at = sent_at

    def render(self) -> str:
        return self.author.render(self.body, self.sent_at)


class ChatHistory:
    """Cliente: monta o histórico a partir da resposta da API e renderiza as mensagens."""

    def __init__(self, authors: AuthorFactory) -> None:
        self._authors = authors
        self.messages: list[Message] = []

    def load(self, payload: Iterable[RawMessage]) -> None:
        for raw in payload:
            self.messages.append(
                Message(
                    id=raw["id"],
                    author=self._authors.get(raw["user"]),
                    body=raw["body"],
                    sent_at=datetime.fromisoformat(raw["sent_at"]),
                )
            )

    def render(self, last: int | None = None) -> str:
        visible = self.messages if last is None else self.messages[-last:]
        return '<ul class="chat">' + "".join(m.render() for m in visible) + "</ul>"

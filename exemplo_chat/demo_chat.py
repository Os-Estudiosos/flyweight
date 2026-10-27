"""Compara o histórico de chat SEM e COM Flyweight.

Uso:  python demo_chat.py [mensagens] [usuarios]      (padrão: 50000 30)
"""

from __future__ import annotations

import gc
import html
import json
import random
import sys
import time
import tracemalloc
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from chat import AuthorFactory, ChatHistory


# ----------------------------------------------------------------------------
# ANTES: cada mensagem guarda a sua própria cópia dos dados do autor.
# (slots=True também aqui, para que a comparação meça só o efeito do Flyweight)
# ----------------------------------------------------------------------------
@dataclass(slots=True)
class NaiveMessage:
    id: int
    body: str
    sent_at: datetime
    author_id: int
    author_name: str
    author_avatar_url: str
    author_color: str
    author_role: str

    def render(self) -> str:
        badge = f' <span class="badge">{html.escape(self.author_role)}</span>' if self.author_role != "member" else ""
        return (
            f'<li class="msg"><img class="avatar" src="{html.escape(self.author_avatar_url)}" alt="" width="32" height="32">'
            f'<strong style="color:{html.escape(self.author_color)}">{html.escape(self.author_name)}</strong>{badge}'
            f'<time datetime="{self.sent_at.isoformat()}">{self.sent_at:%d/%m %H:%M}</time>'
            f"<p>{html.escape(self.body)}</p></li>"
        )


def load_naive(payload: list[dict]) -> list[NaiveMessage]:
    return [
        NaiveMessage(
            id=raw["id"],
            body=raw["body"],
            sent_at=datetime.fromisoformat(raw["sent_at"]),
            author_id=raw["user"]["id"],
            author_name=raw["user"]["name"],
            author_avatar_url=raw["user"]["avatar_url"],
            author_color=raw["user"]["color"],
            author_role=raw["user"]["role"],
        )
        for raw in payload
    ]


# ----------------------------------------------------------------------------
# DEPOIS: Flyweight (ver chat.py)
# ----------------------------------------------------------------------------
def load_flyweight(payload: list[dict]) -> tuple[ChatHistory, AuthorFactory]:
    factory = AuthorFactory()
    history = ChatHistory(factory)
    history.load(payload)
    return history, factory


# ----------------------------------------------------------------------------
# Dados de teste e medição
# ----------------------------------------------------------------------------
FIRST_NAMES = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Felipe", "Gabriela", "Heitor", "Isabela", "João"]
LAST_NAMES = ["Silva", "Souza", "Oliveira", "Pereira", "Costa", "Rodrigues", "Almeida", "Nascimento"]
PHRASES = [
    "Bom dia, pessoal!",
    "Alguém conseguiu rodar o deploy de ontem?",
    "Subi a correção no PR, podem revisar?",
    "Reunião às 15h na sala 2.",
    "Valeu! Funcionou aqui.",
    "Vou almoçar, volto em 1h.",
    "Os testes de integração quebraram de novo :(",
    "Atualizei a documentação da API.",
]


def fake_api_response(n_messages: int, n_users: int, seed: int = 42) -> str:
    """Simula o JSON devolvido pela API: o autor vem embutido em cada mensagem."""
    rng = random.Random(seed)
    users = [
        {
            "id": i,
            "name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
            "avatar_url": f"https://cdn.exemplo.com.br/avatars/{i}/{rng.getrandbits(64):016x}.png?size=64",
            "color": f"#{rng.getrandbits(24):06x}",
            "role": rng.choice(["member"] * 8 + ["moderador", "admin"]),
        }
        for i in range(1, n_users + 1)
    ]
    start = datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc)
    messages = [
        {
            "id": i,
            "body": rng.choice(PHRASES),
            "sent_at": (start + timedelta(minutes=3 * i)).isoformat(),
            "user": rng.choice(users),
        }
        for i in range(1, n_messages + 1)
    ]
    return json.dumps(messages)


def measure_memory(build: Callable[[list[dict]], object], raw_json: str) -> tuple[object, int]:
    """Memória que continua ocupada pelo resultado depois de descartar o payload da API."""
    gc.collect()
    tracemalloc.start()
    payload = json.loads(raw_json)
    result = build(payload)
    del payload
    gc.collect()
    current, _peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, current


def measure_render(render: Callable[[], str]) -> float:
    start = time.perf_counter()
    render()
    return time.perf_counter() - start


def mb(n_bytes: int) -> str:
    return f"{n_bytes / 1024 / 1024:,.1f} MB".replace(".", ",")


def main() -> None:
    n_messages = int(sys.argv[1]) if len(sys.argv) > 1 else 50_000
    n_users = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    raw_json = fake_api_response(n_messages, n_users)

    naive, naive_mem = measure_memory(load_naive, raw_json)
    (history, factory), fly_mem = measure_memory(load_flyweight, raw_json)

    naive_render = measure_render(lambda: "".join(m.render() for m in naive))
    fly_render = measure_render(history.render)

    saving = 1 - fly_mem / naive_mem
    print(f"Histórico: {n_messages:,} mensagens de {n_users} usuários\n".replace(",", "."))
    print(f"{'':32}{'Sem Flyweight':>15}{'Com Flyweight':>16}")
    print(f"{'Memória ocupada pelas mensagens':32}{mb(naive_mem):>15}{mb(fly_mem):>16}   (-{saving:.0%})")
    print(f"{'Objetos com dados de autor':32}{len(naive):>15,}{factory.created:>16,}".replace(",", "."))
    print(f"{'Tempo para renderizar tudo':32}{naive_render * 1000:>12.0f} ms{fly_render * 1000:>13.0f} ms")

    # Todas as mensagens de um mesmo usuário apontam para o MESMO objeto Author.
    first = history.messages[0]
    same_user = [m for m in history.messages if m.author.id == first.author.id]
    print(f"\n{len(same_user)} mensagens de '{first.author.name}' compartilham o mesmo Author? "
          f"{all(m.author is first.author for m in same_user)}")

    # Flyweight é imutável: tentar alterar gera erro.
    try:
        first.author.name = "Outro nome"  # type: ignore[misc]
    except AttributeError as exc:
        print(f"Tentativa de alterar o flyweight: {type(exc).__name__}")

    print("\nHTML da primeira mensagem:")
    print(first.render())

    # Pool com referências fracas: sem mensagens, os autores saem do pool sozinhos.
    del history, first, same_user
    gc.collect()
    print(f"\nAutores no pool depois de descartar o histórico: {len(factory)}")


if __name__ == "__main__":
    main()

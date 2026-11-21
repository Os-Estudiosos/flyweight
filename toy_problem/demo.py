"""Toy problem: editor de texto SEM e COM Flyweight.

Uso:  python toy_problem/demo.py [caracteres]      (padrão: 20000)

Parte 1: digita o mesmo documento nas duas versões e compara a memória.
Parte 2: mostra, num documento pequeno, quais caracteres compartilham o mesmo glifo.
"""

import dataclasses
import sys
import time
import tracemalloc

import editor_com_flyweight as com
import editor_sem_flyweight as sem

TITULO = "Como um editor desenha o texto\n"
PARAGRAFO = [  # (trecho, cor)
    ("Num editor de texto, cada letra que aparece na tela é desenhada a partir de um ", "preto"),
    ("glifo", "vermelho"),
    (". Um livro inteiro usa poucas dezenas de glifos diferentes, mas milhares de ocorrências de cada um.\n", "preto"),
]


def escrever(documento, caracteres: int) -> None:
    """Digita o mesmo conteúdo nas duas versões: um título e parágrafos até completar `caracteres`."""
    documento.digitar(TITULO, fonte="Georgia", tamanho=18, cor="azul")
    while len(documento.caracteres) < caracteres:
        for trecho, cor in PARAGRAFO:
            documento.digitar(trecho[: caracteres - len(documento.caracteres)], cor=cor)


def medir(modulo, caracteres: int):
    inicio = time.perf_counter()
    escrever(modulo.Documento(), caracteres)
    tempo = time.perf_counter() - inicio

    tracemalloc.start()
    documento = modulo.Documento()
    escrever(documento, caracteres)
    memoria, _pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return documento, memoria, tempo


def mb(n_bytes: float) -> str:
    return f"{n_bytes / 1024**2:.1f} MB".replace(".", ",")


def num(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def comparar(caracteres: int) -> None:
    print(f"PARTE 1: documento com {num(caracteres)} caracteres (título em Georgia 18, texto em Arial 12)\n")
    linhas = {}
    for nome, modulo in (("SEM Flyweight", sem), ("COM Flyweight", com)):
        documento, memoria, tempo = medir(modulo, caracteres)
        distintos = {id(d): d for d in documento.desenhos()}
        linhas[nome] = (
            num(len(documento.caracteres)),
            num(len(distintos)),
            mb(sum(len(d) for d in distintos.values())),
            mb(memoria),
            f"{tempo * 1000:.0f} ms",
        )
    rotulos = (
        "Caracteres no documento",
        "Desenhos (bitmaps) na memória",
        "Memória dos desenhos",
        "Memória total do documento",
        "Tempo para digitar",
    )
    print(f"{'':32}{'SEM Flyweight':>15}{'COM Flyweight':>16}")
    for i, rotulo in enumerate(rotulos):
        print(f"{rotulo:32}{linhas['SEM Flyweight'][i]:>15}{linhas['COM Flyweight'][i]:>16}")


def mostrar_mecanismo() -> None:
    print('\nPARTE 2: "casa " (preto) + "casa" (vermelho) + nova linha + "casa" (Georgia 18)\n')
    documento = com.Documento()
    documento.digitar("casa ", cor="preto")
    documento.digitar("casa", cor="vermelho")
    documento.digitar("\ncasa", fonte="Georgia", tamanho=18)

    numeros: dict[int, int] = {}  # id do glifo -> número sequencial, só para exibir
    for caractere in documento.caracteres:
        n = numeros.setdefault(id(caractere.glifo), len(numeros) + 1)
        print(f"  {caractere.desenhar():52} -> glifo #{n}")
    print(f"\n{len(documento.caracteres)} caracteres, {len(documento.fabrica)} glifos na fábrica")

    fabrica = documento.fabrica
    a1 = fabrica.obter("a", "Arial", 12)
    a2 = fabrica.obter("a", "Arial", 12)
    print(f"fabrica.obter('a', 'Arial', 12) devolve sempre o mesmo objeto? {a1 is a2}")
    try:
        a1.fonte = "Times"  # type: ignore[misc]
    except dataclasses.FrozenInstanceError as erro:
        print(f"Tentar alterar um glifo (a1.fonte = 'Times'): {type(erro).__name__}")


def main() -> None:
    caracteres = int(sys.argv[1]) if len(sys.argv) > 1 else 20_000
    comparar(caracteres)
    mostrar_mecanismo()


if __name__ == "__main__":
    main()

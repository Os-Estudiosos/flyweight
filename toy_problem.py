"""Toy problem do Flyweight: alunos e a ementa do curso.

    uv run python toy_problem.py
"""

import sys
from dataclasses import FrozenInstanceError, dataclass


def carregar_ementa(curso):
    """Imagina um arquivo de ~300 KB lido do disco. Cada chamada cria um texto NOVO."""
    return f"ementa completa de {curso}... " * 10_000


# ---------------- SEM Flyweight ----------------

class AlunoSemFlyweight:
    def __init__(self, nome, curso):
        self.nome = nome
        self.curso = curso
        self.ementa = carregar_ementa(curso)    # <-- o problema: uma cópia por aluno


# ---------------- COM Flyweight ----------------

@dataclass(frozen=True)
class Curso:                                    # FLYWEIGHT: estado intrínseco, imutável
    nome: str
    ementa: str

    def descrever(self, aluno):                 # o estado extrínseco chega por parâmetro
        return f"{aluno} cursa {self.nome}"


class CursoFactory:                             # FÁBRICA
    def __init__(self):
        self._pool = {}

    def get(self, nome):
        if nome not in self._pool:              # só na primeira vez
            self._pool[nome] = Curso(nome, carregar_ementa(nome))
        return self._pool[nome]                 # nas outras, devolve o mesmo objeto


class Aluno:                                    # CONTEXTO: estado extrínseco + referência
    __slots__ = ("nome", "curso")

    def __init__(self, nome, curso):
        self.nome = nome
        self.curso = curso                      # referência, não cópia

    def descrever(self):
        return self.curso.descrever(self.nome)


# ---------------- Comparação ----------------

def curso_do(i):
    return "Engenharia" if i % 2 else "Direito"


def ementas_na_memoria(ementas):
    unicas = {id(e): e for e in ementas}.values()
    return len(unicas), sum(sys.getsizeof(e) for e in unicas) / 1024**2


if __name__ == "__main__":
    sem = [AlunoSemFlyweight(f"Aluno {i}", curso_do(i)) for i in range(1000)]

    fabrica = CursoFactory()                    # CLIENTE: o código abaixo
    com = [Aluno(f"Aluno {i}", fabrica.get(curso_do(i))) for i in range(1000)]

    n_sem, mb_sem = ementas_na_memoria(a.ementa for a in sem)
    n_com, mb_com = ementas_na_memoria(a.curso.ementa for a in com)
    print(f"SEM Flyweight: {n_sem:>4} ementas na memória, {mb_sem:6.1f} MB")
    print(f"COM Flyweight: {n_com:>4} ementas na memória, {mb_com:6.1f} MB\n")

    print(com[1].descrever())
    print("sem[1].ementa is sem[3].ementa ->", sem[1].ementa is sem[3].ementa, "(cópias)")
    print("com[1].curso is com[3].curso   ->", com[1].curso is com[3].curso, "(mesmo objeto)")
    try:
        com[1].curso.nome = "Medicina"
    except FrozenInstanceError:
        print("com[1].curso.nome = 'Medicina' -> FrozenInstanceError")

    assert (n_sem, n_com) == (1000, 2)
    assert com[1].curso is com[3].curso and sem[1].ementa is not sem[3].ementa

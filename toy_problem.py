"""Toy problem do Flyweight: alunos e a ementa do curso.

    uv run python toy_problem.py
"""
"""Toy problem do Flyweight: alunos e a ementa do curso."""


def carregar_ementa(curso):
    """Imagina um arquivo de ~200 KB. Cada chamada cria um texto NOVO."""
    return f"ementa completa de {curso}... " * 10_000


# ---------------- SEM Flyweight ----------------

class AlunoSemFlyweight:
    def __init__(self, nome, curso):
        self.nome = nome
        self.curso = curso
        self.ementa = carregar_ementa(curso)


# ---------------- COM Flyweight ----------------

class Curso:
    def __init__(self, nome):
        self.nome = nome
        self.ementa = carregar_ementa(nome)


class CursoFactory:
    def __init__(self):
        self._pool = {}

    def get(self, nome):
        if nome not in self._pool:
            self._pool[nome] = Curso(nome)
        return self._pool[nome]


class Aluno:
    def __init__(self, nome, curso):
        self.nome = nome
        self.curso = curso


# ---------------- Comparação ----------------

def curso_do(i):
    return "Engenharia" if i % 2 else "Direito"


if __name__ == "__main__":
    sem = [AlunoSemFlyweight(f"Aluno {i}", curso_do(i)) for i in range(1000)]

    fabrica = CursoFactory()
    com = [Aluno(f"Aluno {i}", fabrica.get(curso_do(i))) for i in range(1000)]

    print("Sem Flyweight:", len({id(a.ementa) for a in sem}), "ementas na memória")
    print("Com Flyweight:", len({id(a.curso.ementa) for a in com}), "ementas na memória")

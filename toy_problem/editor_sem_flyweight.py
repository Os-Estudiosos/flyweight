"""Toy problem SEM Flyweight: cada caractere guarda tudo.

Cada ocorrência de um caractere guarda o símbolo, a fonte, o
tamanho e o próprio desenho (bitmap), junto com a posição e a
cor. Num documento com 20.000 caracteres existem 20.000
bitmaps, embora só algumas dezenas sejam diferentes.
"""

from rasterizador import rasterizar


class Caractere:
    """Caractere "gordo": dados repetidos e únicos, juntos."""

    __slots__ = ("simbolo", "fonte", "tamanho", "desenho",
                 "linha", "coluna", "cor")

    def __init__(self, simbolo, fonte, tamanho, linha, coluna, cor):
        self.simbolo = simbolo
        self.fonte = fonte
        self.tamanho = tamanho
        # Cada ocorrência rasteriza e guarda o próprio desenho.
        self.desenho = rasterizar(simbolo, fonte, tamanho)
        self.linha = linha
        self.coluna = coluna
        self.cor = cor

    def desenhar(self):
        return (f"{self.simbolo!r} {self.fonte} {self.tamanho}pt "
                f"na posição ({self.linha}, {self.coluna}), "
                f"cor {self.cor}")


class Documento:
    """Guarda os caracteres na ordem em que foram digitados."""

    def __init__(self):
        self.caracteres = []
        self._linha = 0
        self._coluna = 0

    def digitar(self, texto, fonte="Arial", tamanho=12,
                cor="preto"):
        for simbolo in texto:
            if simbolo == "\n":
                self._linha, self._coluna = self._linha + 1, 0
                continue
            self.caracteres.append(
                Caractere(simbolo, fonte, tamanho,
                          self._linha, self._coluna, cor))
            self._coluna += 1

    def desenhos(self):
        """Desenho usado por cada caractere (para as métricas)."""
        return [c.desenho for c in self.caracteres]

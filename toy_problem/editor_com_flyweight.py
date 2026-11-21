"""Toy problem COM Flyweight: os caracteres compartilham glifos.

Separação do estado:
  - intrínseco -> Glifo: símbolo, fonte, tamanho e desenho
    (compartilhado e imutável)
  - extrínseco -> Caractere: linha, coluna e cor
    (único de cada ocorrência)
A FabricaDeGlifos garante um único Glifo por combinação de
símbolo, fonte e tamanho.
"""

from dataclasses import dataclass, field

from rasterizador import rasterizar


@dataclass(frozen=True, slots=True)
class Glifo:
    """Flyweight: o que é igual em todas as ocorrências."""

    simbolo: str
    fonte: str
    tamanho: int
    desenho: bytes = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        # Única escrita permitida: o desenho é feito uma vez.
        object.__setattr__(
            self, "desenho",
            rasterizar(self.simbolo, self.fonte, self.tamanho))

    def desenhar(self, linha, coluna, cor):
        """O estado extrínseco chega por parâmetro."""
        return (f"{self.simbolo!r} {self.fonte} {self.tamanho}pt "
                f"na posição ({linha}, {coluna}), cor {cor}")


class FabricaDeGlifos:
    """Fábrica: devolve o Glifo existente ou cria um novo."""

    def __init__(self):
        self._glifos = {}  # (simbolo, fonte, tamanho) -> Glifo

    def obter(self, simbolo, fonte, tamanho):
        chave = (simbolo, fonte, tamanho)
        if chave not in self._glifos:
            self._glifos[chave] = Glifo(simbolo, fonte, tamanho)
        return self._glifos[chave]

    def __len__(self):
        return len(self._glifos)


class Caractere:
    """Contexto: posição e cor desta ocorrência + o glifo."""

    __slots__ = ("linha", "coluna", "cor", "glifo")

    def __init__(self, linha, coluna, cor, glifo):
        self.linha = linha
        self.coluna = coluna
        self.cor = cor
        self.glifo = glifo  # referência ao glifo compartilhado

    def desenhar(self):
        return self.glifo.desenhar(self.linha, self.coluna, self.cor)


class Documento:
    """Cliente: posiciona os caracteres e pede glifos à fábrica."""

    def __init__(self):
        self.fabrica = FabricaDeGlifos()
        self.caracteres = []
        self._linha = 0
        self._coluna = 0

    def digitar(self, texto, fonte="Arial", tamanho=12,
                cor="preto"):
        for simbolo in texto:
            if simbolo == "\n":
                self._linha, self._coluna = self._linha + 1, 0
                continue
            glifo = self.fabrica.obter(simbolo, fonte, tamanho)
            self.caracteres.append(
                Caractere(self._linha, self._coluna, cor, glifo))
            self._coluna += 1

    def desenhos(self):
        """Desenho usado por cada caractere (para as métricas)."""
        return [c.glifo.desenho for c in self.caracteres]

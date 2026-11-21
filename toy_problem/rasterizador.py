"""Desenho (bitmap) de um glifo, usado pelas duas versões do editor.

Num editor de verdade, o contorno do caractere vem do arquivo da fonte e é
convertido em pixels. Aqui o desenho é simulado: o que importa é que ele é
(1) pesado e (2) igual para todas as ocorrências do mesmo símbolo, fonte e tamanho.
"""

import zlib

DPI = 300  # resolução de impressão


def rasterizar(simbolo: str, fonte: str, tamanho: int) -> bytes:
    """Devolve a máscara do glifo: 1 byte por pixel, dizendo o quanto o pixel é coberto.

    A cor não entra aqui: ela é aplicada só na hora de desenhar.
    Ex.: 12 pt a 300 dpi -> 50 x 50 pixels -> 2.500 bytes.
    """
    lado = round(tamanho * DPI / 72)  # 1 pt = 1/72 de polegada
    semente = zlib.crc32(f"{simbolo}|{fonte}|{tamanho}".encode())
    linha = bytes((semente >> (i % 24)) % 256 for i in range(lado))
    return linha * lado

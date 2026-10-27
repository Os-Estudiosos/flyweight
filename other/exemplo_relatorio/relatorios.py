"""Geração de relatórios HTML (gráfico Plotly + tabela) para abrir no celular."""

from __future__ import annotations

import html
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

import plotly.graph_objects as go
from plotly.offline import get_plotlyjs, get_plotlyjs_version

from other.exemplo_relatorio.assets import Asset, SharedAssetStore

CSS_FILE = Path(__file__).with_name("relatorio.css")


def plotly_asset() -> Asset:
    return Asset("plotly", get_plotlyjs_version(), get_plotlyjs().encode("utf-8"))


def css_asset() -> Asset:
    return Asset("relatorio", "1", CSS_FILE.read_bytes(), content_type="text/css")


@dataclass(frozen=True)
class Report:
    """Estado extrínseco: tudo o que é único de cada relatório."""

    title: str
    generated_at: datetime
    figure: go.Figure
    columns: Sequence[str]
    rows: Sequence[Sequence[object]]


class AssetTags(Protocol):
    def script(self, asset: Asset) -> str: ...
    def stylesheet(self, asset: Asset) -> str: ...


class InlineAssetTags:
    """ANTES: copia o conteúdo inteiro de cada biblioteca para dentro do HTML."""

    def script(self, asset: Asset) -> str:
        return f"<script>{asset.content.decode('utf-8')}</script>"

    def stylesheet(self, asset: Asset) -> str:
        return f"<style>{asset.content.decode('utf-8')}</style>"


class SharedAssetTags:
    """DEPOIS (Flyweight): o HTML guarda só a referência (URL) da cópia compartilhada."""

    def __init__(self, store: SharedAssetStore) -> None:
        self._store = store

    def script(self, asset: Asset) -> str:
        return f'<script src="{html.escape(self._store.url_for(asset))}"></script>'

    def stylesheet(self, asset: Asset) -> str:
        return f'<link rel="stylesheet" href="{html.escape(self._store.url_for(asset))}">'


def _cell(value: object) -> str:
    if isinstance(value, int):
        return f'<td class="num">{value:,}</td>'.replace(",", ".")
    if isinstance(value, float):
        brl = f"{value:,.2f}".translate(str.maketrans(",.", ".,"))
        return f'<td class="num">R$ {brl}</td>'
    return f"<td>{html.escape(str(value))}</td>"


class ReportRenderer:
    """Monta o HTML de um relatório. Quem decide como as bibliotecas entram na
    página (embutidas ou compartilhadas) é o objeto `tags` recebido."""

    def __init__(self, tags: AssetTags, plotly: Asset | None = None, css: Asset | None = None) -> None:
        self._tags = tags
        self._plotly = plotly or plotly_asset()
        self._css = css or css_asset()

    def render(self, report: Report) -> str:
        chart = report.figure.to_html(
            full_html=False,
            include_plotlyjs=False,  # a biblioteca entra pelo <head>, abaixo
            config={"responsive": True, "displaylogo": False},
        )
        header = "".join(f"<th>{html.escape(c)}</th>" for c in report.columns)
        body = "".join("<tr>" + "".join(_cell(v) for v in row) + "</tr>" for row in report.rows)
        return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(report.title)}</title>
{self._tags.stylesheet(self._css)}
{self._tags.script(self._plotly)}
</head>
<body>
<h1>{html.escape(report.title)}</h1>
<p class="meta">Gerado em {report.generated_at:%d/%m/%Y %H:%M}</p>
<div class="chart">{chart}</div>
<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>
</body>
</html>
"""

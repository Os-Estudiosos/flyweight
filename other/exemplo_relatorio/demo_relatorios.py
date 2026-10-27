"""Gera os mesmos relatórios ANTES (bibliotecas embutidas em cada HTML) e DEPOIS
(Flyweight: bibliotecas num storage compartilhado) e compara os tamanhos.

Uso:  python demo_relatorios.py [quantidade_de_relatorios]      (padrão: 40)

Saída em ./saida:
  antes/    relatórios com o Plotly e o CSS embutidos
  depois/   relatórios que só referenciam as bibliotecas
  storage/  a única cópia das bibliotecas (no mundo real: S3/CDN)
Abra saida/depois/loja_01.html no navegador para ver o relatório funcionando.
"""

from __future__ import annotations

import random
import shutil
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import plotly.graph_objects as go

from other.exemplo_relatorio.assets import LocalStorage, SharedAssetStore
from other.exemplo_relatorio.relatorios import InlineAssetTags, Report, ReportRenderer, SharedAssetTags, css_asset, plotly_asset

OUT = Path(__file__).with_name("saida")

# Premissas da estimativa de rede (ajuste para a sua realidade):
VIEWS = 5_000  # aberturas de relatórios no período
DEVICES = 300  # celulares distintos; cada um baixa as bibliotecas uma vez e guarda em cache

PRODUCTS = ["Café 500g", "Arroz 5kg", "Feijão 1kg", "Óleo 900ml", "Açúcar 1kg", "Leite 1L",
            "Macarrão 500g", "Farinha 1kg", "Sabão em pó", "Detergente", "Papel higiênico", "Biscoito"]


def fake_sales_report(store: int, rng: random.Random) -> Report:
    days = [date(2026, 9, 1) + timedelta(days=d) for d in range(30)]
    fig = go.Figure(go.Bar(x=[d.isoformat() for d in days], y=[round(rng.uniform(8e3, 25e3), 2) for _ in days]))
    fig.update_layout(title="Vendas diárias (R$)", height=320, margin=dict(l=48, r=12, t=40, b=40))
    rows = sorted(
        ((p, rng.randint(40, 900), round(rng.uniform(500, 30_000), 2)) for p in PRODUCTS),
        key=lambda r: r[2],
        reverse=True,
    )
    return Report(
        title=f"Loja {store:02d} - vendas de setembro/2026",
        generated_at=datetime(2026, 10, 1, 6, 0),
        figure=fig,
        columns=["Produto", "Quantidade", "Faturamento"],
        rows=rows,
    )


def write_all(renderer: ReportRenderer, reports: list[Report], folder: Path) -> int:
    folder.mkdir(parents=True)
    total = 0
    for i, report in enumerate(reports, start=1):
        path = folder / f"loja_{i:02d}.html"
        path.write_text(renderer.render(report), encoding="utf-8")
        total += path.stat().st_size
    return total


def fmt(n_bytes: float) -> str:
    for unit, size in (("GB", 1024**3), ("MB", 1024**2), ("KB", 1024)):
        if n_bytes >= size:
            return f"{n_bytes / size:.2f} {unit}".replace(".", ",")
    return f"{n_bytes:.0f} B"


def num(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def main() -> None:
    n_reports = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    rng = random.Random(42)
    reports = [fake_sales_report(i, rng) for i in range(1, n_reports + 1)]

    if OUT.exists():
        shutil.rmtree(OUT)
    plotly, css = plotly_asset(), css_asset()

    # ANTES: cada HTML leva uma cópia inteira das bibliotecas.
    before = write_all(ReportRenderer(InlineAssetTags(), plotly, css), reports, OUT / "antes")

    # DEPOIS: as bibliotecas vão uma única vez para o storage; o HTML guarda só a URL.
    # Em produção: SharedAssetStore(S3Storage("meu-bucket", "https://cdn.minhaempresa.com.br"))
    store = SharedAssetStore(LocalStorage(OUT / "storage", base_url="../storage"))
    after = write_all(ReportRenderer(SharedAssetTags(store), plotly, css), reports, OUT / "depois")
    libs = sum(f.stat().st_size for f in (OUT / "storage").rglob("*") if f.is_file())

    avg_before, avg_after = before / n_reports, after / n_reports
    print(f"{n_reports} relatórios gerados em {OUT}\n")
    print(f"{'':28}{'ANTES (embutido)':>18}{'DEPOIS (Flyweight)':>22}")
    print(f"{'Tamanho médio por HTML':28}{fmt(avg_before):>18}{fmt(avg_after):>22}")
    print(f"{'Total dos HTMLs':28}{fmt(before):>18}{fmt(after):>22}")
    print(f"{'Cópias das bibliotecas':28}{n_reports:>18}{1:>22}   ({fmt(libs)} no storage)")
    print(f"{'Uploads para o storage':28}{'-':>18}{store.uploads:>22}   ({store.reused} reaproveitamentos)")

    net_before = VIEWS * avg_before
    net_after = VIEWS * avg_after + DEVICES * libs
    print(f"\nRede estimada para {num(VIEWS)} aberturas em {num(DEVICES)} celulares:")
    print(f"  ANTES : {num(VIEWS)} x {fmt(avg_before)} = {fmt(net_before)}")
    print(f"  DEPOIS: {num(VIEWS)} x {fmt(avg_after)} + {num(DEVICES)} x {fmt(libs)} (1o acesso; depois, cache)"
          f" = {fmt(net_after)}   (-{1 - net_after / net_before:.0%})")


if __name__ == "__main__":
    main()

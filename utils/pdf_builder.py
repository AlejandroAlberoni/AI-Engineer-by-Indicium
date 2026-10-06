import uuid
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from fontTools.ttLib import TTFont
import matplotlib.pyplot as plt
from fpdf import FPDF

FONT_DIR = Path(matplotlib.get_data_path()) / "fonts" / "ttf"

OUTPUT_DIR = Path("/tmp/relatorios")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

fonte_ttf = FONT_DIR / "DejaVuSans.ttf"
GLIFOS = set(TTFont(str(fonte_ttf)).getBestCmap().keys())

def _extract_series(dados: dict) -> tuple[list, list]:
    """Extrai (labels, values) de saídas no formato das tools de dados:
    {"casos_diarios": {"25-08": 12, ...}} ou {"casos_mensais": {"09-2025": 340, ...}}.
    """
    for chave in ("casos_diarios", "casos_mensais"):
        if chave in dados:
            serie = dados[chave]
            return list(serie.keys()), list(serie.values())
    raise ValueError(f"Formato de dados inesperado, chaves recebidas: {list(dados.keys())}")


def _plot_chart(titulo: str, labels: list, values: list, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(labels, values, marker="o")
    ax.set_title(titulo)
    ax.tick_params(axis="x", rotation=45, labelsize=7)
    if len(labels) > 15:
        passo = max(1, len(labels) // 15)
        for i, tick in enumerate(ax.get_xticklabels()):
            if i % passo != 0:
                tick.set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

def sanitizar(texto: str) -> str:
    return "".join(
        c if (c in ("\n", "\t") or ord(c) in GLIFOS) else "?"
        for c in texto
    )

def build_pdf(data: str, comentario: str, dados_graficos: dict) -> str:
    run_id = uuid.uuid4().hex[:8]
    work_dir = OUTPUT_DIR / run_id
    work_dir.mkdir(parents=True, exist_ok=True)

    # 1. gera as imagens dos gráficos
    chart_paths = {}
    titulos = {
        "casos_ultimo_mes": "Casos diários (últimos 30 dias)",
        "casos_ultimo_ano": "Casos mensais (últimos 12 meses)",
    }
    for chave, dados in dados_graficos.items():
        labels, values = _extract_series(dados)
        img_path = work_dir / f"{chave}.png"
        _plot_chart(titulos.get(chave, chave), labels, values, img_path)
        chart_paths[chave] = img_path

    # 2. monta o PDF
    pdf = FPDF()
    pdf.add_font("DejaVu", "", str(FONT_DIR / "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", str(FONT_DIR / "DejaVuSans-Bold.ttf"))
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "Relatório SRAG", ln=True)
    pdf.set_font("DejaVu", "", 10)
    pdf.cell(0, 8, f"Data de referência: {data}", ln=True)
    pdf.ln(4)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 8, "Comentário", ln=True)
    pdf.set_font("DejaVu", "", 10)
    pdf.multi_cell(0, 6, sanitizar(comentario), markdown=True)
    pdf.ln(4)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 8, "Gráficos", ln=True)
    for img_path in chart_paths.values():
        pdf.image(str(img_path), w=170)
        pdf.ln(4)

    pdf_path = work_dir / "relatorio.pdf"
    pdf.output(str(pdf_path))
    return str(pdf_path)
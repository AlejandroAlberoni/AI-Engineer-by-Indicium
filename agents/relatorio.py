from langgraph.graph import StateGraph, START, END

from agents.researcher import researcher
from utils.pdf_builder import build_pdf

from schemas import RelatorioInput, RelatorioOutput, RelatorioState

from tools import numero_mensal_casos_ultimo_ano, numero_casos_ultimo_mes
import asyncio

GRAFICO_TOOLS = {
    "casos_ultimo_mes": numero_casos_ultimo_mes,
    "casos_ultimo_ano": numero_mensal_casos_ultimo_ano,
}

async def gerar_comentario(state: RelatorioState):
    try:
        out = await researcher.ainvoke({"data": state["data"]})
    except:
        return {"comentario": "Não foi possível gerar o comentário."}
    return {"comentario": out["answer"]}

async def coletar_dados_graficos(data: str) -> dict:
    resultados = await asyncio.gather(
        *(tool.ainvoke({"data": data}) for tool in GRAFICO_TOOLS.values())
    )
    return dict(zip(GRAFICO_TOOLS, resultados))

async def coletar_graficos(state: RelatorioState):
    try: 
        dados = await coletar_dados_graficos(state["data"])
    except:
        {"dados_graficos": "Erro na coleta dos dados graficos"}
    return {"dados_graficos": dados}


async def montar_pdf(state: RelatorioState):
    path = build_pdf(
        data=state["data"],
        comentario=state["comentario"],
        dados_graficos=state["dados_graficos"],
    )
    return {"pdf_path": path}


g = StateGraph(
    RelatorioState,
    input_schema=RelatorioInput,
    output_schema=RelatorioOutput,
)

g.add_node("comentario", gerar_comentario)
g.add_node("graficos", coletar_graficos)
g.add_node("montar_pdf", montar_pdf)

g.add_edge(START, "comentario")
g.add_edge(START, "graficos")
g.add_edge(["comentario", "graficos"], "montar_pdf")
g.add_edge("montar_pdf", END)

relatorio_graph = g.compile(name="relatorio").with_config(
    run_name="relatorio",
    tags=["workflow:relatorio"],
    metadata={"agent": "relatorio"},
)
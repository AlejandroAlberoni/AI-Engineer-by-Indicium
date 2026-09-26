from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig 
from langchain_core.tools import InjectedToolCallId

from langgraph.types import Command

from typing import Annotated

from agents.relatorio import relatorio_graph

@tool
async def gerar_relatorio_srag(
    data: str,
    config: RunnableConfig,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Gera um relatório em PDF sobre SRAG para a data informada, com
    comentário sobre as métricas e gráficos de casos e óbitos.
 
    Use quando o usuário pedir um relatório, documento ou PDF sobre SRAG.
    Se ele não informou a data, pergunte antes de chamar esta tool.
 
    Args:
        data: data de referência no formato ISO (YYYY-MM-DD).
    """
    out = await relatorio_graph.ainvoke({"data": data}, config=config)
    return Command(update={
        "pdf_path": out["pdf_path"],
        "messages": [ToolMessage(
            content=f"Relatório gerado com sucesso para {data}.",
            tool_call_id=tool_call_id,
        )],
    })
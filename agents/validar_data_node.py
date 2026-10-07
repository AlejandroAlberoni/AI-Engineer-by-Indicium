from langgraph.types import Command
from langgraph.graph import MessagesState, END
from langchain.messages import AIMessage

from typing import Literal, Optional
from pydantic import BaseModel

from llm import llm

from tools import _load_df

class _Data(BaseModel):
    data_iso: Optional[str] = None

_extrator = llm.with_structured_output(_Data)
def validar_data_node(state: MessagesState) -> Command[Literal["orchestrator", "__end__"]]:
    df = _load_df().copy()
    texto = state["messages"][-1].content
    try:
        r = _extrator.invoke(
            f"Extraia a data do texto para formato ISO -> AAAA-MM-DD "
            f"Se não houver data clara, retorne null.\n\n{texto}"
        )
        d = r.data_iso

        data_max = df["DT_NOTIFIC"].max()
        data_min = df["DT_NOTIFIC"].min()
        if not (data_min <= d <= data_max):
            return Command(
                goto=END,
                update={"messages": [AIMessage(
                    content=f"Data inválida. Tente uma data no range: ({data_min} a {data_max})."
                )]},
            )
    except Exception:
        return Command(
            goto=END,
            update={"messages": [AIMessage(
                content="Não identifiquei uma data válida. Tente novamente com uma data válida."
            )]},
        )
    return Command(goto="orchestrator")
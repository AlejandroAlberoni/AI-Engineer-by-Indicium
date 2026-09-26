from pydantic import BaseModel, Field
from typing import TypedDict, List

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class ResearcherInput(TypedDict):
    data: str

class ResearcherOutput(TypedDict):
    answer: str

class MetricQueries(BaseModel):
    metrica: str = Field(description="Nome da métrica a que estas queries se referem")
    queries: List[str] = Field(
        description="Exatamente 2 queries de pesquisa web para esta métrica",
        min_length=2,
        max_length=2,
    )

class SearchQueries(BaseModel):
    itens: List[MetricQueries] = Field(
        description="Uma entrada para cada métrica recebida"
    )

class ResearcherState(ResearcherInput, ResearcherOutput):
    metricas: dict
    queries: list[MetricQueries]
    web_results: list

class RelatorioRequest(BaseModel):
    data: str

class RelatorioInput(TypedDict):
    data: str
 
 
class RelatorioOutput(TypedDict):
    pdf_path: str
 
 
class RelatorioState(RelatorioInput, RelatorioOutput):
    comentario: str
    dados_graficos: dict
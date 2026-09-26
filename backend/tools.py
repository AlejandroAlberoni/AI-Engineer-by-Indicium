from dotenv import load_dotenv

load_dotenv()

from langchain.tools import tool

from functools import lru_cache
import pandas as pd
from datetime import date, timedelta
import os
from tavily import TavilyClient


tavily = TavilyClient(
    api_key = os.getenv("TAVILY_API_KEY")
)


@lru_cache(maxsize=1)
def _load_df() -> pd.DataFrame:
    CSV_PATH = "INFLUD25_DATASUS-Versao26-06-2025.csv"
    print("Carregando CSV na cache...")
    return pd.read_csv(CSV_PATH, sep=";")


@tool
def taxa_aumento_casos(data: str) -> str:
    """
    Taxa de aumento de casos.

    Use esta ferramenta para responder perguntas sobre a taxa de aumento de casos da SRAG.
    """
    df = _load_df()
    casos_data = df[df['DT_NOTIFIC'] <= data]

    casos_data = casos_data.dropna(subset=['CLASSI_FIN'])

    total = (casos_data['CLASSI_FIN'] == 5).sum()
    taxa = total / len(casos_data)

    taxa = round(taxa * 100, 2)

    result = {
        "metric": "taxa_aumento_casos",
        "value": taxa,
        "unit": "%",
        "date": data
    }

    return result

@tool
def taxa_mortalidade(data: str = str(date.today())) -> str:
    """
    Taxa de mortalidade total.

    Use esta ferramenta para responder perguntas sobre a porcentagem ou taxa de pessoas que vieram à óbito pela SRAG.
    """
    df = _load_df()

    casos_data = df[df['DT_NOTIFIC'] <= data]

    casos_data = casos_data.dropna(subset=["EVOLUCAO"])

    casos = (casos_data['EVOLUCAO'] == 2).sum()
    taxa = casos / len(casos_data)

    taxa = round((taxa * 100), 2)

    result = {
        "metric": "taxa_mortalidade",
        "value": taxa,
        "unit": "%",
        "date": data
    }

    return result

@tool
def taxa_ocupacao_UTI(data: str = str(date.today())) -> str:
    """
    Taxa de ocupação de UTI.

    Use esta ferramenta para responder perguntas sobre a taxa de ocupação de UTI pela SRAG.
    """
    df = _load_df()

    ocupacao_data = df[df['DT_NOTIFIC'] <= data]

    ocupacao_data = ocupacao_data.dropna(subset=["UTI"])

    ocupacao = (ocupacao_data["UTI"] == 1).sum()

    taxa = ocupacao / len(ocupacao_data)

    taxa = round((taxa * 100), 2)

    result = {
        "metric": "taxa_ocupacao_UTI",
        "value": taxa,
        "unit": "%",
        "date": data
    }

    return result

@tool
def taxa_vacinacao_populacao(data: str = str(date.today())) -> str:
    """
    Taxa de vacinação total da população.

    Use esta ferramenta para responder sobre a taxa de vacinação da população.
    """
    df = _load_df()

    vacinados_data = df[df['DT_NOTIFIC'] <= data]

    vacinados_data = vacinados_data.dropna(subset=['VACINA_COV'])

    vacinados = (vacinados_data['VACINA_COV'] == 1).sum()

    taxa = vacinados / len(vacinados_data)

    taxa = round((taxa * 100), 2)

    result = {
        "metric": "taxa_vacinacao_populacao",
        "value": taxa,
        "unit": "%",
        "date": data
    }

    return result


@tool
def numero_casos_ultimo_mes(data: str = str(date.today())) -> dict:
    """
    Número diário de casos registrados nos últimos 30 dias.

    Use esta ferramenta para responder perguntas sobre o número de casos
    registrados no último mês.
    """
    df = _load_df()

    df["DT_NOTIFIC"] = pd.to_datetime(
        df["DT_NOTIFIC"],
        errors="coerce"
    )

    data = pd.to_datetime(data)
    data_inicio = data - timedelta(days=30)

    casos_data = df[
        (df["DT_NOTIFIC"] >= data_inicio) &
        (df["DT_NOTIFIC"] <= data)
    ]

    casos_diarios = (
        casos_data
        .groupby(casos_data["DT_NOTIFIC"].dt.normalize())
        .size()
    )

    todos_os_dias = pd.date_range(
        start=data_inicio,
        end=data,
        freq="D"
    )

    casos_diarios = (
        casos_diarios
        .reindex(todos_os_dias, fill_value=0)
    )

    resultado = {
        dia.strftime("%d-%m"): int(casos)
        for dia, casos in casos_diarios.items()
    }

    result = {
        "data_inicio": data_inicio.strftime("%Y-%m-%d"),
        "data_fim": data.strftime("%Y-%m-%d"),
        "casos_diarios": resultado
    }

    return result


@tool
def numero_mensal_casos_ultimo_ano(data: str = str(date.today())) -> dict:
    """
    Número mensal de casos registrados durante os últimos 12 meses.

    Use esta ferramenta para responder perguntas sobre o número de casos registrados nos últimos 12 meses.
    """
    df = _load_df()

    df["DT_NOTIFIC"] = pd.to_datetime(
        df["DT_NOTIFIC"],
        errors="coerce"
    )

    data = pd.to_datetime(data)

    fim = data.replace(day=1)

    inicio = fim - pd.DateOffset(months=11)

    casos_data = df[
        (df["DT_NOTIFIC"] >= inicio) &
        (df["DT_NOTIFIC"] < fim + pd.DateOffset(months=1))
    ]

    casos_data = casos_data.copy()
    casos_data["mes"] = casos_data["DT_NOTIFIC"].dt.to_period("M")

    casos_mensais = casos_data.groupby("mes").size()

    todos_os_meses = pd.period_range(
        start=inicio,
        end=fim,
        freq="M"
    )

    casos_mensais = casos_mensais.reindex(
        todos_os_meses,
        fill_value=0
    )

    resultado = {
        mes.strftime("%m-%Y"): int(casos)
        for mes, casos in casos_mensais.items()
    }


    result = {
        "data_inicio": inicio.strftime("%Y-%m-%d"),
        "data_fim": data.strftime("%Y-%m-%d"),
        "casos_mensais": resultado
    }

    return result

@tool
def pesquisa_web(
    query: str,
    data_inicio: str,
    data_fim: str,
):
    """
    Pesquisa noticias na internet.

    Use esta ferramenta para resgatar informações.

    query:
        Consulta que será pesquisada.

    data_inicio:
        Data inicial da pesquisa no formato YYYY-MM-DD

    data_fim:
        Data final da pesquisa no formato YYYY-MM-DD
    """
    response = tavily.search(
        query=query,
        start_date=data_inicio,
        end_date=data_fim,
        search_depth="basic",
        max_results=4
    )
    result = [
        {
            "title": result["title"],
            "url": result["url"],
            "content": result["content"]
        }
        for result in response["results"]
    ]

    return result

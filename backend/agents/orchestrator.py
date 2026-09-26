from llm import llm
from langgraph.graph import MessagesState

from agents.prompts import ORCHESTRATOR_PROMPT

from utils.relatorio_tool import gerar_relatorio_srag

ORCHESTRATOR_TOOLS = [
    gerar_relatorio_srag
]

llm_with_tools = llm.bind_tools(ORCHESTRATOR_TOOLS)

def orchestrator(state: MessagesState):
    """
    Agente orquestrador do sistema.
    """

    messages = [
        {
            "role": "system",
            "content": ORCHESTRATOR_PROMPT,
        },
        *state["messages"],
    ]

    response = llm_with_tools.invoke(messages)

    return { "messages": [response] }
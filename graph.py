from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from agents.orchestrator import orchestrator, ORCHESTRATOR_TOOLS
from agents.validar_data_node import validar_data_node

from typing import Optional


class MainState(MessagesState):
    pdf_path: Optional[str]



builder = StateGraph(MainState)
# Valida a entrada antes de executar o fluxo
builder.add_node("validar_data", validar_data_node)

builder.add_node("orchestrator", orchestrator)

builder.add_node("orchestrator_tools", ToolNode(ORCHESTRATOR_TOOLS))


builder.add_edge(START, "validar_data")

builder.add_conditional_edges(
    "orchestrator",
    tools_condition,
    {
        "tools": "orchestrator_tools",
        "__end__": END,
    },
)

builder.add_edge("orchestrator_tools", "orchestrator")


graph = builder.compile()
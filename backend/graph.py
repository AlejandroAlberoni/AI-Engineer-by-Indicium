from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from agents.orchestrator import orchestrator, ORCHESTRATOR_TOOLS

from typing import Optional


class MainState(MessagesState):
    pdf_path: Optional[str]



builder = StateGraph(MainState)
builder.add_node("orchestrator", orchestrator)

builder.add_node("orchestrator_tools", ToolNode(ORCHESTRATOR_TOOLS))


builder.add_edge(START, "orchestrator")

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
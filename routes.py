from fastapi import APIRouter
from fastapi.responses import FileResponse
from schemas import ChatRequest, ChatResponse
from graph import graph

from observability.langfuse import langfuse_handler

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        config = {
            "callbacks": [langfuse_handler],
            "run_name": "chat",
        }

        result = await graph.ainvoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config=config,
        )

        if result.get("pdf_path"):
            return FileResponse(
                result["pdf_path"],
                media_type="application/pdf",
                filename="relatorio_srag.pdf",
            )

        last_message = result["messages"][-1]
        return ChatResponse(response=last_message.text)

    except Exception as e:
        print(str(e))
        raise
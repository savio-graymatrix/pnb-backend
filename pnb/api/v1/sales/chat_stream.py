from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pnb.services.generic.generate_chat_response import generate_chat_responses
from pnb.langgraph.sales.workflows import SALES_GRAPHS

router = APIRouter(prefix="/chat_stream", tags=["Sales · Chat Stream"])


@router.get("/")
async def sales_chatbot(message: str, checkpoint_id: str = Query(None)):
    return StreamingResponse(
        generate_chat_responses(
            graph=SALES_GRAPHS["sales_chatbot"],
            message=message,
            checkpoint_id=checkpoint_id,
            checkpoint_required=False,
        ),
        headers={"Content-Type": "text/event-stream"},
    )
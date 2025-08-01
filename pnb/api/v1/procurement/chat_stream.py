from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pnb.services.generic.generate_chat_response import generate_chat_responses
from pnb.langgraph.procurement.workflows import PROCUREMENT_GRAPHS

router = APIRouter(prefix="/chat_stream", tags=["Procurement · Chat Stream"])


@router.get("/")
async def chat_stream(message: str, checkpoint_id: str = Query(None)):
    return StreamingResponse(
        generate_chat_responses(
            graph=PROCUREMENT_GRAPHS["tender"],
            message=message,
            checkpoint_id=checkpoint_id,
            checkpoint_required=True,
        ),
        headers={"Content-Type": "text/event-stream"},
    )

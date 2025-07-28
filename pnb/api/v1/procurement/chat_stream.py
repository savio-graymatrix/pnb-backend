from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pnb.services.procurement_generate_chat_response import generate_chat_responses

router = APIRouter(prefix="/chat_stream", tags=["Procurement · Chat Stream"])


@router.get("/{message}")
async def chat_stream(message: str, checkpoint_id: str = Query(None)):
    return StreamingResponse(
        generate_chat_responses(
            message=message,
            checkpoint_id=checkpoint_id  
        ),
        headers={"Content-Type": "text/event-stream"},
    )

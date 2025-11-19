from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pnb.services.credit_assist.generate_chat_responses import generate_chat_responses

router = APIRouter(prefix="/chat_stream", tags=["Credit Assist · Chat Stream"])


@router.get("/")
async def chat_stream(message: str, checkpoint_id: str = Query(None)):
    return StreamingResponse(
        generate_chat_responses(message=message, checkpoint_id=checkpoint_id),
        headers={"Content-Type": "text/event-stream"},
    )

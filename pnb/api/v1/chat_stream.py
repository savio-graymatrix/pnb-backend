from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse


router = APIRouter(prefix="/chat_stream", tags=["Chat Stream"])

@router.get("/{message}")
async def chat_stream(message: str, checkpoint_id: str = Query(None)):
    return StreamingResponse(headers={"Content-Type":"text/event-stream"})
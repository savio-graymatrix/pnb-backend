from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pnb.services.soc.soc_generate_chat_responses import generate_chat_responses

router = APIRouter(prefix="/soc_chat_stream", tags=["SOC · Chat Stream"])


@router.get("/")
async def soc_chat_stream(message: str, checkpoint_id: str = Query(None)):
    return StreamingResponse(
        generate_chat_responses(message=message, checkpoint_id=checkpoint_id),
        headers={"Content-Type": "text/event-stream"},
    )

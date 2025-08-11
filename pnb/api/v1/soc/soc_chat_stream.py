from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pnb.services.soc.soc_generate_chat_responses import generate_chat_responses

router = APIRouter(prefix="/soc_chat_stream", tags=["SOC · Chat Stream"])

@router.get("/{message}")
async def soc_chat_stream(
    message: str,
    checkpoint_id: str = Query(None),
    collection: str = Query(..., description="The name of the incident report collection to search within")
):
    return StreamingResponse(
        generate_chat_responses(
            message=message,
            checkpoint_id=checkpoint_id,
            collection=collection
        ),
        headers={"Content-Type": "text/event-stream"},
    )

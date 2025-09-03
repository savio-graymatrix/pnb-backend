from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List
from pnb.langgraph.debt_collection.agents.summarizer_agent import TranscriptAgent

router = APIRouter(prefix="/summarizer", tags=["Debt Collection · Summarizer"])


@router.post("/")
async def summarize_transcript(transcript: dict):
    result = await TranscriptAgent.agent({"transcript": transcript["transcript"]})
    return JSONResponse(content=result.model_dump(), status_code=200)

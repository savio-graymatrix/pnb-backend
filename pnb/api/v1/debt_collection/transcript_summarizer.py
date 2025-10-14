from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List
from pnb.langgraph.debt_collection.agents.summarizer_agent import TranscriptAgent
from pydantic import BaseModel

router = APIRouter(prefix="/summarizer", tags=["Debt Collection · Summarizer"])


class DebtTranscript(BaseModel):
    transcript: List


# @router.post("/")
# async def summarize_transcript(transcript: dict):
#     result = await TranscriptAgent.agent({"transcript": transcript["transcript"]})
#     return JSONResponse(content=result.model_dump(), status_code=200)
@router.post("/")
async def summarize_transcript(transcript: DebtTranscript):
    result = await TranscriptAgent.agent({"transcript": transcript.transcript})
    return JSONResponse(content=result.model_dump(), status_code=200)

from fastapi import APIRouter, HTTPException, Body, Depends, Query
from typing import List, Optional
from pnb.db.data_models import Instruction, UpdateInstruction, File
from pnb.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
    parse_operator_filter,
)
from datetime import datetime, timezone
from beanie.operators import Set
from pnb.langgraph.debt_collection.agents.summarizer_agent import TranscriptAgent

router = APIRouter(prefix="/summarizer", tags=["Debt Collection · Summarizer"])


@router.post("/")
async def summarize_transcript(transcript: List[dict]):
    result = await TranscriptAgent.agent({"transcript": transcript})
    return result["summary"]

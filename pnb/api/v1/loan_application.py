from fastapi import APIRouter, HTTPException, Body
from typing import List
from pnb.db.data_models import Instruction, UpdateInstruction, File
from pnb.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
    parse_operator_filter,
)
from datetime import datetime, timezone
from beanie.operators import Set
from pnb.langgraph.agents.instruction_agent import InstructionAgent

router = APIRouter(prefix="/loan_application")

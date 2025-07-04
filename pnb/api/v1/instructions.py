from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List
from pnb.db.data_models import CreateInstruction, Instruction, UpdateInstruction
from pnb.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
    parse_operator_filter,
)
from typing import Optional
from datetime import datetime, timezone
from beanie.operators import Set

router = APIRouter(prefix="/instructions", tags=["Instructions"])

@router.post("/")
async def create_instruction(instruction: CreateInstruction):
    instruction = Instruction(**instruction.model.dump())
    await instruction.insert()
    return instruction

# Get All Instructions
@router.get("/")
async def get_all_instructions():
    pass


# Get Instruction by ID
# @router.get("/{bid_id}", response_model=Instruction)
@router.get("/{instruction_id}", response_model=Instruction)
async def get_instruction(instruction_id: str):
    instruction = await Instruction.get(instruction_id)
    if not instruction:
        raise HTTPException(status_code=404, detail="Instruction not found")
    return instruction


# Update Instruction
@router.put("/{instruction_id}", response_model=Instruction)
async def update_instruction(instruction_id: str, data: Instruction):
    instruction = await Instruction.get(instruction_id)
    if not instruction:
        raise HTTPException(status_code=404, detail="Instruction not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(instruction, field, value)

    instruction.updated_at = datetime.now(timezone.utc)
    await instruction.save()
    return instruction


# Delete Instruction
@router.delete("/{instruction_id}")
async def delete_instruction(instruction_id: str):
    instruction = await Instruction.get(instruction_id)
    if not instruction:
        raise HTTPException(status_code=404, detail="Instruction not found")
    await instruction.delete()
    return {"detail": "Instruction deleted"}


# Patch Instruction
@router.patch("/{instruction_id}", response_model=Instruction)
async def patch_instruction(instruction_id: str, data: UpdateInstruction = Body(...)):
    instruction = await Instruction.get(instruction_id)
    if not instruction:
        raise HTTPException(status_code=404, detail="Instruction not found")
    instruction.updated_at = datetime.now(timezone.utc)
    await instruction.update(
        Set(
            {getattr(Instruction, f): v for f, v in data.model_dump(exclude_unset=True).items()}
        )
    )
    return instruction
from fastapi import APIRouter, HTTPException, Body, Depends,Query
from typing import List, Optional
from pnb.db.data_models import Instruction, UpdateInstruction, File
from pnb.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
    parse_operator_filter,
)
from datetime import datetime, timezone
from beanie.operators import Set
from pnb.langgraph.credit_assist.agents.instruction_agent import InstructionAgent

router = APIRouter(prefix="/instructions", tags=["Credit Assist · Instructions"])


@router.post("/")
async def create_instruction(instructions: List[Instruction]):
    created_instructions = list()
    for instruction in instructions:
        instruction_obj = Instruction(**instruction.model.dump())
        await instruction_obj.insert()
        created_instructions.append(instruction)
    return created_instructions


# Get All Instructions
@router.get("/")
async def get_all_instructions(
    pagination: CursorPaginationRequest = Depends(),
    created_at: Optional[str] = Query(None),
):
    query = {}
    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    cursor = Instruction.find(query).sort((sort_field, sort_order))

    if pagination.after_id:
        after_bid = await Instruction.get(pagination.after_id)
        if after_bid:
            after_value = getattr(after_bid, sort_field)
            query[sort_field] = {"$lt" if sort_order == -1 else "$gt": after_value}
            cursor = Instruction.find(query).sort((sort_field, sort_order))

    items = await cursor.limit(pagination.limit).to_list()

    next_cursor = items[-1].id if len(items) == pagination.limit else None

    return CursorPaginationResponse[Instruction](items=items, next_cursor=next_cursor)


# Get Instruction by ID
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
            {
                getattr(Instruction, f): v
                for f, v in data.model_dump(exclude_unset=True).items()
            }
        )
    )
    return instruction


# Generate Instructions
@router.post("/generate")
async def generate_instructions(files: List[File] = Body(...)):
    master_instruction_list = list()
    for file in files:
        config = {"configurable": {"thread_id": 1, "file": file.url}}
        result = await InstructionAgent.instruction_agent(
            {"messages": []}, config=config
        )
        instruction_list = [
            await Instruction(content=instruction).insert()
            for instruction in result.instruction_set
        ]
        master_instruction_list.extend(instruction_list)
    # mis_obj = await Instruction.insert_many(master_instruction_list)
    # print(mis_obj)
    return master_instruction_list

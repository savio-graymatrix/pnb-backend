from fastapi import APIRouter, HTTPException, Body, Query, Depends
from typing import List, Optional
from pnb.db.data_models import LoanApplication, UpdateLoanApplication 
from pnb.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
    parse_operator_filter,
)
from datetime import datetime, timezone
from beanie.operators import Set
from pnb.langgraph.agents.instruction_agent import InstructionAgent

router = APIRouter(prefix="/loan_application",tags=["Loan Application"])

# Create Loan Applications
@router.post("/")
async def create_application(applications: List[LoanApplication]):
    created_applications = list()
    for application in applications:
        application_obj = LoanApplication(**application.model.dump())
        await application_obj.insert()
        created_applications.append(application_obj)
    return created_applications


# Get All Loan Instructions
@router.get("/")
async def get_all_applications(
    pagination: CursorPaginationRequest = Depends(),
    created_at: Optional[str] = Query(None),
):
    query = {}
    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    cursor = LoanApplication.find(query).sort((sort_field, sort_order))

    if pagination.after_id:
        after_bid = await LoanApplication.get(pagination.after_id)
        if after_bid:
            after_value = getattr(after_bid, sort_field)
            query[sort_field] = {"$lt" if sort_order == -1 else "$gt": after_value}
            cursor = LoanApplication.find(query).sort((sort_field, sort_order))

    items = await cursor.limit(pagination.limit).to_list()

    next_cursor = items[-1].id if len(items) == pagination.limit else None

    return CursorPaginationResponse[LoanApplication](items=items, next_cursor=next_cursor)


# Get Loan Application by ID
@router.get("/{application_id}", response_model=LoanApplication)
async def get_application(application_id: str):
    loan_application = await LoanApplication.get(application_id)
    if not loan_application:
        raise HTTPException(status_code=404, detail="Instruction not found")
    return loan_application


# Update Loan Application
@router.put("/{application_id}", response_model=LoanApplication)
async def update_instruction(application_id: str, data: LoanApplication):
    loan_application = await LoanApplication.get(application_id)
    if not loan_application:
        raise HTTPException(status_code=404, detail="Instruction not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(loan_application, field, value)

    loan_application.updated_at = datetime.now(timezone.utc)
    await loan_application.save()
    return loan_application


# Delete Loan Application
@router.delete("/{application_id}")
async def delete_instruction(application_id: str):
    loan_application = await LoanApplication.get(application_id)
    if not loan_application:
        raise HTTPException(status_code=404, detail="Instruction not found")
    await loan_application.delete()
    return {"detail": "Instruction deleted"}


# Patch Loan Application
@router.patch("/{application_id}", response_model=LoanApplication)
async def patch_instruction(application_id: str, data: UpdateLoanApplication = Body(...)):
    loan_application = await LoanApplication.get(application_id)
    if not loan_application:
        raise HTTPException(status_code=404, detail="Instruction not found")
    loan_application.updated_at = datetime.now(timezone.utc)
    await loan_application.update(
        Set(
            {
                getattr(LoanApplication, f): v
                for f, v in data.model_dump(exclude_unset=True).items()
            }
        )
    )
    return loan_application

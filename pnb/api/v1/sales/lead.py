from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List
from pnb.db.data_models import Lead
from pnb.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
    parse_operator_filter,
)
from beanie import PydanticObjectId
from typing import Optional
from datetime import datetime, timezone
from beanie.operators import Set


router = APIRouter(prefix="/lead", tags=["Sales · Leads"])


@router.get("/")
async def get_all_leads(
    pagination: CursorPaginationRequest = Depends(),
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
):
    query = {}
    if status:
        query["status"] = status
    if source:
        query["source"] = source
    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    cursor = Lead.find(query).sort((sort_field, sort_order))

    if pagination.after_id:
        after_bid = await Lead.get(pagination.after_id)
        if after_bid:
            after_value = getattr(after_bid, sort_field)
            query[sort_field] = {"$lt" if sort_order == -1 else "$gt": after_value}
            cursor = Lead.find(query).sort((sort_field, sort_order))

    items = await cursor.limit(pagination.limit).to_list()

    next_cursor = items[-1].id if len(items) == pagination.limit else None

    return CursorPaginationResponse[Lead](items=items, next_cursor=next_cursor)


@router.get("/{lead_id}", response_model=Lead)
async def get_review(lead_id: PydanticObjectId):
    lead = await Lead.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Instruction not found")
    return lead


# Create Loan Applications
@router.post("/")
async def create_leads(leads: List[Lead]):
    created_leads = list()
    for lead in leads:
        lead_obj = Lead(**lead.model_dump())
        created_leads.append(lead_obj)
    await Lead.insert_many(created_leads)
    return created_leads

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List
from pnb.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
    parse_operator_filter,
)
from beanie import PydanticObjectId
from typing import Optional
from datetime import datetime, timezone
from beanie.operators import Set
from pnb.db.data_models import Tender, UpdateTender


router = APIRouter(prefix="/tender", tags=["Procurement · Tender"])


@router.get("/")
async def get_all_tenders(
    pagination: CursorPaginationRequest = Depends(),
    created_at: Optional[str] = Query(None),
):
    query = {}
    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    cursor = Tender.find(query).sort((sort_field, sort_order))

    if pagination.after_id:
        after_bid = await Tender.get(pagination.after_id)
        if after_bid:
            after_value = getattr(after_bid, sort_field)
            query[sort_field] = {"$lt" if sort_order == -1 else "$gt": after_value}
            cursor = Tender.find(query).sort((sort_field, sort_order))

    items = await cursor.limit(pagination.limit).to_list()

    next_cursor = items[-1].id if len(items) == pagination.limit else None

    return CursorPaginationResponse[Tender](
        items=items, next_cursor=next_cursor
    )


@router.get("/{tender_id}", response_model=Tender)
async def get_tender(tender_id: str):
    tender = await Tender.get(tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail=f"{Tender.__class__.__name__} not found")
    return tender


@router.put("/{tender_id}")
async def update_tender(tender_id: str, data: UpdateTender):
    tender = await Tender.get(tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail=f"{Tender.__class__.__name__} not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tender, field, value)

    tender.updated_at = datetime.now(timezone.utc)
    await tender.save()
    return tender


@router.delete("/{tender_id}")
async def delete_tender(tender_id: str):
    tender = await Tender.get(tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail=f"{Tender.__class__.__name__} not found")
    await tender.delete()
    return {"detail": "Instruction deleted"}


@router.patch("/{tender_id}")
async def patch_tender(tender_id: str, data: UpdateTender = Body(...)):
    tender = await Tender.get(tender_id)
    update_data = data.model_dump(exclude_unset=True)
    if not tender:
        raise HTTPException(status_code=404, detail=f"{Tender.__class__.__name__} not found")
    tender.updated_at = datetime.now(timezone.utc)
    await tender.update(Set(update_data))
    return tender

from fastapi import APIRouter, HTTPException, Query as FastAPIQuery, Depends, Body, UploadFile, File as FastAPIFile
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
from pnb.db.data_models.procurement.TenderRule import UpdateTenderRule, TenderRule



router = APIRouter(prefix="/tender_rule", tags=["Procurement · Tender Rule"])

@router.post("/generate")
async def generate_tender_rule(files: List[UploadFile] = FastAPIFile(...)):
    pass

@router.get("/")
async def get_all_tender_rules(
    pagination: CursorPaginationRequest = Depends(),
    tender_id: Optional[PydanticObjectId] = FastAPIQuery(None)
):
    tender_rule = {}
    if tender_id:
        tender_rule["tender_id"] = tender_id
    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    cursor = TenderRule.find(tender_rule).sort((sort_field, sort_order))

    if pagination.after_id:
        after_bid = await TenderRule.get(pagination.after_id)
        if after_bid:
            after_value = getattr(after_bid, sort_field)
            tender_rule[sort_field] = {"$lt" if sort_order == -1 else "$gt": after_value}
            cursor = TenderRule.find(tender_rule).sort((sort_field, sort_order))

    items = await cursor.limit(pagination.limit).to_list()

    next_cursor = items[-1].id if len(items) == pagination.limit else None

    return CursorPaginationResponse[TenderRule](items=items, next_cursor=next_cursor)


@router.get("/{query_id}", response_model=TenderRule)
async def get_query(query_id: PydanticObjectId):
    tender_rule = await TenderRule.get(query_id)
    if not tender_rule:
        raise HTTPException(
            status_code=404, detail=f"{TenderRule.__class__.__name__} not found"
        )
    return tender_rule


@router.put("/{query_id}")
async def update_query(query_id: PydanticObjectId, data: UpdateTenderRule):
    tender_rule = await TenderRule.get(query_id)
    if not tender_rule:
        raise HTTPException(
            status_code=404, detail=f"{TenderRule.__class__.__name__} not found"
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tender_rule, field, value)

    tender_rule.updated_at = datetime.now(timezone.utc)
    await tender_rule.save()
    return tender_rule


@router.delete("/{query_id}")
async def delete_query(query_id: PydanticObjectId):
    tender_rule = await TenderRule.get(query_id)
    if not tender_rule:
        raise HTTPException(
            status_code=404, detail=f"{TenderRule.__class__.__name__} not found"
        )
    await tender_rule.delete()
    return {"detail": "Instruction deleted"}


@router.patch("/{query_id}")
async def patch_query(query_id: PydanticObjectId, data: UpdateTenderRule = Body(...)):
    tender_rule = await TenderRule.get(query_id)
    update_data = data.model_dump(exclude_unset=True)
    if not tender_rule:
        raise HTTPException(
            status_code=404, detail=f"{TenderRule.__class__.__name__} not found"
        )
    tender_rule.updated_at = datetime.now(timezone.utc)
    await tender_rule.update(Set(update_data))
    return tender_rule

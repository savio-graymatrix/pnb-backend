from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List
from pnb.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
)
from beanie import PydanticObjectId
from typing import Optional
from datetime import datetime, timezone
from beanie.operators import Set
from pnb.db.data_models import Bid, UpdateBid, CreateBid
from bson import ObjectId
from pnb.langgraph.procurement.agents.review_agent import ReviewAgent


router = APIRouter(prefix="/bids", tags=["Procurement · Bids"])

@router.post("/")
async def create_bids(bids: List[UpdateBid]):
    created_bid = list()
    for bid in bids:
        bid_obj = Bid(**bid.model_dump(exclude_unset=True))
        # if not bid.response:
        #     bid_obj.response = ""
        await bid_obj.insert()
        # result = await ReviewAgent.review(
        #     {"messages": []},
        #     config={
        #         "configurable": {"thread_id": query.tender, "query_id": query_obj.id}
        #     },
        # )
        # query_obj.response = result.answer
        await bid_obj.save()
        created_bid.append(bid_obj)
    return created_bid


@router.get("/")
async def get_all_bids(
    pagination: CursorPaginationRequest = Depends(),
    created_at: Optional[str] = Query(None),
    tender_id: Optional[str] = Query(None)
):
    query = {}
    if tender_id:
        query['tender.$id'] = ObjectId(tender_id)
    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    cursor = Bid.find(query).sort((sort_field, sort_order))

    if pagination.after_id:
        after_bid = await Bid.get(pagination.after_id)
        if after_bid:
            after_value = getattr(after_bid, sort_field)
            query[sort_field] = {"$lt" if sort_order == -1 else "$gt": after_value}
            cursor = Bid.find(query).sort((sort_field, sort_order))

    items = await cursor.limit(pagination.limit).to_list()

    next_cursor = items[-1].id if len(items) == pagination.limit else None

    return CursorPaginationResponse[Bid](items=items, next_cursor=next_cursor)


@router.get("/{bid_id}", response_model=Bid)
async def get_bid(bid_id: PydanticObjectId):
    bid = await Bid.get(bid_id)
    if not bid:
        raise HTTPException(
            status_code=404, detail=f"{Bid.__class__.__name__} not found"
        )
    return bid


@router.put("/{bid_id}")
async def update_bid(bid_id: PydanticObjectId, data: UpdateBid):
    bid = await Bid.get(bid_id)
    if not bid:
        raise HTTPException(
            status_code=404, detail=f"{Bid.__class__.__name__} not found"
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bid, field, value)

    bid.updated_at = datetime.now(timezone.utc)
    await bid.save()
    return bid


@router.delete("/{bid_id}")
async def delete_bid(bid_id: PydanticObjectId):
    bid = await Bid.get(bid_id)
    if not bid:
        raise HTTPException(
            status_code=404, detail=f"{Bid.__class__.__name__} not found"
        )
    await bid.delete()
    return {"detail": "Instruction deleted"}


@router.patch("/{bid_id}")
async def patch_bid(bid_id: PydanticObjectId, data: UpdateBid = Body(...)):
    bid = await Bid.get(bid_id)
    update_data = data.model_dump(exclude_unset=True)
    if not bid:
        raise HTTPException(
            status_code=404, detail=f"{Bid.__class__.__name__} not found"
        )
    bid.updated_at = datetime.now(timezone.utc)
    await bid.update(Set(update_data))
    return bid

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List
from pnb.db.data_models import ReviewSet, Review, ReviewSetResponse
from beanie import DeleteRules


from pnb.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
    parse_operator_filter,
)
from typing import Optional
from datetime import datetime, timezone
from beanie import PydanticObjectId

router = APIRouter(prefix="/review-set",tags=["Review Set"])

@router.get("/{review_set_id}/reviews")
async def get_reviews_by_set_id(review_set_id: PydanticObjectId):
    review_set = await ReviewSet.get(review_set_id)
    if not review_set:
        raise HTTPException(status_code=404, detail="Instruction not found")
    reviews = Review.find({"review_set_id":review_set.id})
    return ReviewSetResponse(**review_set.model_dump(),reviews=reviews)

@router.get("/")
async def get_review_sets():
    
    pass

@router.post("/generate/{bid_id}")
async def generate_reviews(bid_id: PydanticObjectId):
    pass

@router.delete("/{review_set_id}")
async def delete_review_set(review_set_id: PydanticObjectId):
    review_set = await ReviewSet.get(review_set_id)
    if not review_set:
        raise HTTPException(status_code=404, detail="Instruction not found")
    await review_set.delete(link_rule=DeleteRules.DELETE_LINKS)
    return {"detail": "Instruction deleted"}

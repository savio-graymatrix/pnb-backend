from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List
from pnb.db.data_models import Review, UpdateReview
from pnb.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
    parse_operator_filter,
)
from beanie import PydanticObjectId
from typing import Optional
from datetime import datetime, timezone
from beanie.operators import Set


router = APIRouter(prefix="/review", tags=["Credit Assist · Reviews"])


@router.get("/")
async def get_all_reviews(
    pagination: CursorPaginationRequest = Depends(),
    created_at: Optional[str] = Query(None),
    review_set_id: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None),
):
    query = {}
    if review_set_id:
        query["review_set_id"] = PydanticObjectId(review_set_id)
    if review_status:
        query.update(parse_operator_filter("review_status", review_status))
    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    cursor = Review.find(query).sort((sort_field, sort_order))

    if pagination.after_id:
        after_bid = await Review.get(pagination.after_id)
        if after_bid:
            after_value = getattr(after_bid, sort_field)
            query[sort_field] = {"$lt" if sort_order == -1 else "$gt": after_value}
            cursor = Review.find(query).sort((sort_field, sort_order))

    items = await cursor.limit(pagination.limit).to_list()

    next_cursor = items[-1].id if len(items) == pagination.limit else None

    return CursorPaginationResponse[Review](items=items, next_cursor=next_cursor)


@router.get("/{review_id}", response_model=Review)
async def get_review(review_id: PydanticObjectId):
    review = await Review.get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Instruction not found")
    return review


@router.put("/{review_id}")
async def update_review(review_id: PydanticObjectId, data: Review):
    review = await Review.get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Instruction not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    review.updated_at = datetime.now(timezone.utc)
    await review.save()
    return review


@router.delete("/{review_id}")
async def delete_review(review_id: PydanticObjectId):
    review = await Review.get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Instruction not found")
    await review.delete()
    return {"detail": "Instruction deleted"}


@router.patch("/{review_id}")
async def patch_review(review_id: PydanticObjectId, data: UpdateReview = Body(...)):
    review = await Review.get(review_id)
    update_data = data.model_dump(exclude_unset=True)
    if not review:
        raise HTTPException(status_code=404, detail="Instruction not found")
    review.updated_at = datetime.now(timezone.utc)
    # await review.set(
    #     Set(
    #         {
    #             getattr(Review, f): v
    #             for f, v in data.model_dump(exclude_unset=True).items()
    #         }
    #     )
    # )
    await review.update(Set(update_data))
    return review

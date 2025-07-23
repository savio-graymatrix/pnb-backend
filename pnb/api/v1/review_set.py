from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List
from pnb.db.data_models import (
    ReviewSet,
    Review,
    ReviewSetResponse,
    DocumentChecklist,
    AgentLifeCycle,
    LoanApplication,
)
from beanie import DeleteRules


from pnb.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
    parse_operator_filter,
)
from typing import Optional
from datetime import datetime, timezone
from beanie import PydanticObjectId

router = APIRouter(prefix="/review-set", tags=["Review Set"])


@router.get("/latest-review/{application_id}")
async def get_reviews_by_application_id(application_id: PydanticObjectId):
    review_set = (
        await ReviewSet.find(
            ReviewSet.application_id == PydanticObjectId(application_id)
            )
        .sort("-created_at")
        .limit(1)
        .to_list()
    )
    print(review_set)
    if len(review_set) == 0:
        raise HTTPException(
            status_code=404, detail="Review Set for Loan Application not found"
        )
    review_set = await ReviewSet.get(review_set[0].id)
    if not review_set:
        raise HTTPException(status_code=404, detail="Instruction not found")
    reviews = await Review.find({"review_set_id": review_set.id}).to_list()
    agent_lifecycle = await AgentLifeCycle.find(
        {"review_set_id": review_set.id}
    ).to_list()
    document_checklist = await DocumentChecklist.find(
        {"review_set_id": review_set.id}
    ).to_list()
    return ReviewSetResponse(
        application_id=review_set.application_id,
        reviews=reviews,
        agent_lifecycle=agent_lifecycle,
        document_checklist=document_checklist,
    )


@router.get("/{review_set_id}/reviews")
async def get_reviews_by_set_id(review_set_id: PydanticObjectId):
    review_set = await ReviewSet.get(review_set_id)
    if not review_set:
        raise HTTPException(status_code=404, detail="Instruction not found")
    reviews = await Review.find({"review_set_id": review_set.id}).to_list()
    agent_lifecycle = await AgentLifeCycle.find(
        {"review_set_id": review_set.id}
    ).to_list()
    document_checklist = await DocumentChecklist.find(
        {"review_set_id": review_set.id}
    ).to_list()
    return ReviewSetResponse(
        application_id=review_set.application_id,
        reviews=reviews,
        agent_lifecycle=agent_lifecycle,
        document_checklist=document_checklist,
    )


@router.get("/")
async def get_review_sets(
    pagination: CursorPaginationRequest = Depends(),
    created_at: Optional[str] = Query(None),
    application_id: Optional[str] = Query(None),
):
    query = {}
    if application_id:
        query.update({"application_id": PydanticObjectId(application_id)})
    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    cursor = ReviewSet.find(query).sort((sort_field, sort_order))

    if pagination.after_id:
        after_bid = await ReviewSet.get(pagination.after_id)
        if after_bid:
            after_value = getattr(after_bid, sort_field)
            query[sort_field] = {"$lt" if sort_order == -1 else "$gt": after_value}
            cursor = ReviewSet.find(query).sort((sort_field, sort_order))

    items = await cursor.limit(pagination.limit).to_list()

    next_cursor = items[-1].id if len(items) == pagination.limit else None

    return CursorPaginationResponse[ReviewSet](items=items, next_cursor=next_cursor)


# @router.post("/generate/{bid_id}")
# async def generate_reviews(bid_id: PydanticObjectId):
#     pass


@router.delete("/{review_set_id}")
async def delete_review_set(review_set_id: PydanticObjectId):
    review_set = await ReviewSet.get(review_set_id)
    if not review_set:
        raise HTTPException(status_code=404, detail="Instruction not found")
    await review_set.delete(link_rule=DeleteRules.DELETE_LINKS)
    return {"detail": "Instruction deleted"}

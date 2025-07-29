from fastapi import APIRouter, HTTPException, Query as FastAPIQuery, Depends, Body
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
from pnb.db.data_models.procurement.Query import Query, UpdateQuery


router = APIRouter(prefix="/query", tags=["Procurement · Query"])

router.post("/")
async def create_queries(queries: List[Query]):
    created_query = list()
    for query in queries:
        query_obj = Query(**query.model_dump())
        await query_obj.insert()
        created_query.append(query_obj)
    return created_query


@router.get("/")
async def get_all_queries(
    pagination: CursorPaginationRequest = Depends(),
    tender_id: Optional[PydanticObjectId] = FastAPIQuery(None)
):
    query = {}
    if tender_id:
        query["tender_id"] = tender_id
    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    cursor = Query.find(query).sort((sort_field, sort_order))

    if pagination.after_id:
        after_bid = await Query.get(pagination.after_id)
        if after_bid:
            after_value = getattr(after_bid, sort_field)
            query[sort_field] = {"$lt" if sort_order == -1 else "$gt": after_value}
            cursor = Query.find(query).sort((sort_field, sort_order))

    items = await cursor.limit(pagination.limit).to_list()

    next_cursor = items[-1].id if len(items) == pagination.limit else None

    return CursorPaginationResponse[Query](items=items, next_cursor=next_cursor)


@router.get("/{query_id}", response_model=Query)
async def get_query(query_id: PydanticObjectId):
    query = await Query.get(query_id)
    if not query:
        raise HTTPException(
            status_code=404, detail=f"{Query.__class__.__name__} not found"
        )
    return query


@router.put("/{query_id}")
async def update_query(query_id: PydanticObjectId, data: UpdateQuery):
    query = await Query.get(query_id)
    if not query:
        raise HTTPException(
            status_code=404, detail=f"{Query.__class__.__name__} not found"
        )
    # config = {
    #     "configurable": {
    #         "thread_id": query_id,
    #     }
    # }
    # result = await QueryAgent.query_agent(query_id, config)
    # updated_query = result["structured_response"]

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(query, field, value)

    query.updated_at = datetime.now(timezone.utc)
    await query.save()
    return query


@router.delete("/{query_id}")
async def delete_query(query_id: PydanticObjectId):
    query = await Query.get(query_id)
    if not query:
        raise HTTPException(
            status_code=404, detail=f"{Query.__class__.__name__} not found"
        )
    await query.delete()
    return {"detail": "Instruction deleted"}


@router.patch("/{query_id}")
async def patch_query(query_id: PydanticObjectId, data: UpdateQuery = Body(...)):
    query = await Query.get(query_id)
    update_data = data.model_dump(exclude_unset=True)
    if not query:
        raise HTTPException(
            status_code=404, detail=f"{Query.__class__.__name__} not found"
        )
    query.updated_at = datetime.now(timezone.utc)
    await query.update(Set(update_data))
    return query

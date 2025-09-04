from fastapi import APIRouter, HTTPException, Query, Depends
from pnb.db.data_models import Lead
from pnb.db.data_models.sales.Customer import Customer
from pnb.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
    parse_operator_filter,
)
from beanie import PydanticObjectId


router = APIRouter(prefix="/customer", tags=["Sales · Customer"])


@router.get("/")
async def get_all_customers(
    pagination: CursorPaginationRequest = Depends(),
):
    query = {}
    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    cursor = Customer.find(query).sort((sort_field, sort_order))

    if pagination.after_id:
        after_bid = await Customer.get(pagination.after_id)
        if after_bid:
            after_value = getattr(after_bid, sort_field)
            query[sort_field] = {"$lt" if sort_order == -1 else "$gt": after_value}
            cursor = Customer.find(query).sort((sort_field, sort_order))

    items = await cursor.limit(pagination.limit).to_list()

    next_cursor = items[-1].id if len(items) == pagination.limit else None

    return CursorPaginationResponse[Customer](items=items, next_cursor=next_cursor)


@router.get("/{customer_id}", response_model=Lead)
async def get_customer(customer_id: PydanticObjectId):
    customer = await Customer.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

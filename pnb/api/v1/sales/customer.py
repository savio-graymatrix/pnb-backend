from fastapi import APIRouter, HTTPException, Query, Depends
from pnb.db.data_models import Lead
from pnb.db.data_models.sales.Customer import Customer
from pnb.db.utils import (
    PagePaginationMetadata,
    PagePaginationRequest,
    PagePaginationResponse,
)
from beanie import PydanticObjectId
from math import ceil


router = APIRouter(prefix="/customer", tags=["Sales · Customer"])


@router.get("/")
async def get_all_customers(
    pagination: PagePaginationRequest = Depends(),
):
    query = {}

    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    # total count for pagination metadata
    total_items = await Customer.find(query).count()
    total_pages = ceil(total_items / pagination.page_size) if total_items > 0 else 1

    # calculate skip
    skip = (pagination.page - 1) * pagination.page_size

    # fetch items
    items = (
        await Customer.find(query)
        .sort((sort_field, sort_order))
        .skip(skip)
        .limit(pagination.page_size)
        .to_list()
    )

    return PagePaginationResponse[Customer](
        items=items,
        pagination=PagePaginationMetadata(
            currentPage=pagination.page,
            itemsPerPage=pagination.page_size,
            totalItems=total_items,
            totalPages=total_pages,
            hasNextPage=pagination.page < total_pages,
            hasPreviousPage=pagination.page > 1,
        ),
    )


@router.get("/{customer_id}", response_model=Lead)
async def get_customer(customer_id: PydanticObjectId):
    customer = await Customer.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List
from pnb.db.data_models import Lead
from pnb.db.data_models.sales.Product import Product
from pnb.db.utils import (
    PagePaginationRequest,
    PagePaginationResponse,
    PagePaginationMetadata,
)
from beanie import PydanticObjectId
from typing import Optional
from math import ceil

router = APIRouter(prefix="/lead", tags=["Sales · Leads"])


@router.get("/")
async def get_all_leads(
    pagination: PagePaginationRequest = Depends(),
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

    # total count for metadata
    total_items = await Lead.find(query).count()
    total_pages = ceil(total_items / pagination.page_size) if total_items > 0 else 1

    # calculate skip
    skip = (pagination.page - 1) * pagination.page_size

    # fetch leads
    items = (
        await Lead.find(query)
        .sort((sort_field, sort_order))
        .skip(skip)
        .limit(pagination.page_size)
        .to_list()
    )

    return PagePaginationResponse[Lead](
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


@router.get("/{lead_id}", response_model=Lead)
async def get_lead(lead_id: PydanticObjectId):
    lead = await Lead.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


# # Create Loan Applications
# @router.post("/")
# async def create_leads(leads: List[Lead]):
#     created_leads = list()
#     for lead in leads:
#         lead_obj = Lead(**lead.model_dump())
#         created_leads.append(lead_obj)
#     await Lead.insert_many(created_leads)
#     return created_leads


@router.post("/")
async def create_lead(leads: List[Lead]):
    created_leads = []
    for lead in leads:
        lead_data = lead.model_dump()

        # Handle product name if provided
        if "product" in lead_data and lead_data["product"] is not None:
            product_name = lead_data["product"]
            # Search for product by name
            product = await Product.find_one(Product.name == product_name)
            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with name '{product_name}' not found. Please provide a valid product name.",
                )
            print(f"{product = }")
            # Replace the name with the actual product document
            lead_data["product"] = product

        # Create the lead with the processed data
        lead_obj = Lead(**lead_data)
        created_leads.append(lead_obj)

    if created_leads:
        await Lead.insert_many(created_leads)
    return created_leads

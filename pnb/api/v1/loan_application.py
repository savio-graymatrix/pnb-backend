from fastapi import APIRouter, HTTPException, Body, Query, Depends
from typing import List, Optional
from pnb.db.data_models import (
    LoanApplication,
    UpdateLoanApplication,
    Review,
    ReviewSet,
    CreditResponse,
    AgentLifeCycle,
    DocumentChecklist
)
from pnb.db.utils import CursorPaginationRequest, CursorPaginationResponse
from datetime import datetime, timezone
from beanie.operators import Set
from pnb.langgraph.workflows import GRAPHS
from pnb.langgraph.agents.credit_agent import CreditAgent
from pnb import LOGGER
from pnb.langgraph.tools.extractor import store_text_embedding

router = APIRouter(prefix="/loan_application", tags=["Loan Application"])


# Create Loan Applications
@router.post("/")
async def create_application(applications: List[LoanApplication]):
    created_applications = list()
    for application in applications:
        application_obj = LoanApplication(**application.model_dump())
        await application_obj.insert()
        for document in application_obj.documents:
            await store_text_embedding(application_obj.id,str(document[1]))
        created_applications.append(application_obj)
    return created_applications


# Get All Loan Instructions
@router.get("/")
async def get_all_applications(
    pagination: CursorPaginationRequest = Depends(),
    created_at: Optional[str] = Query(None),
):
    query = {}
    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    cursor = LoanApplication.find(query).sort((sort_field, sort_order))

    if pagination.after_id:
        after_bid = await LoanApplication.get(pagination.after_id)
        if after_bid:
            after_value = getattr(after_bid, sort_field)
            query[sort_field] = {"$lt" if sort_order == -1 else "$gt": after_value}
            cursor = LoanApplication.find(query).sort((sort_field, sort_order))

    items = await cursor.limit(pagination.limit).to_list()

    next_cursor = items[-1].id if len(items) == pagination.limit else None

    return CursorPaginationResponse[LoanApplication](
        items=items, next_cursor=next_cursor
    )


# Get Loan Application by ID
@router.get("/{application_id}", response_model=LoanApplication)
async def get_application(application_id: str):
    loan_application = await LoanApplication.get(application_id)
    if not loan_application:
        raise HTTPException(status_code=404, detail="Loan Application not found")
    return loan_application


# Update Loan Application
@router.put("/{application_id}", response_model=LoanApplication)
async def update_application(application_id: str, data: LoanApplication):
    loan_application = await LoanApplication.get(application_id)
    if not loan_application:
        raise HTTPException(status_code=404, detail="Loan Application not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(loan_application, field, value)

    loan_application.updated_at = datetime.now(timezone.utc)
    await loan_application.save()
    return loan_application


# Delete Loan Application
@router.delete("/{application_id}")
async def delete_application(application_id: str):
    loan_application = await LoanApplication.get(application_id)
    if not loan_application:
        raise HTTPException(status_code=404, detail="Loan Application not found")
    await loan_application.delete()
    return {"detail": "Instruction deleted"}


# Patch Loan Application
@router.patch("/{application_id}", response_model=LoanApplication)
async def patch_application(
    application_id: str, data: UpdateLoanApplication = Body(...)
):
    loan_application = await LoanApplication.get(application_id)
    if not loan_application:
        raise HTTPException(status_code=404, detail="Loan Application not found")
    loan_application.updated_at = datetime.now(timezone.utc)
    await loan_application.update(
        Set(
            {
                getattr(LoanApplication, f): v
                for f, v in data.model_dump(exclude_unset=True).items()
            }
        )
    )
    return loan_application


@router.post("/review")
async def review_loan_application(application: LoanApplication = Body(...)):
    # print(application)
    config = {
        "configurable": {
            "thread_id": application.id,
            "metadata": application.model_dump(),
        }
    }
    result = await CreditAgent.credit_agent(
        {
            "messages": [],  # Initialize with empty messages # Pass loan details directly
        },
        config=config,
    )
    review_set = ReviewSet(application_id=application.id)
    await review_set.insert()
    credit_response = CreditResponse(
        review_set=[],
        agent_lifecycle=[],
        documents_checklist=[]
    )
    for review in result.review_set:
        review_obj = Review(**review.model_dump(),review_set_id=review_set.id)
        await review_obj.insert()
        credit_response.review_set.append(review_obj)
    for agent in result.agent_lifecycle:
        agent_obj = AgentLifeCycle(**agent.model_dump(),review_set_id=review_set.id)
        await agent_obj.insert()
        credit_response.agent_lifecycle.append(agent_obj)
    for document in result.documents_checklist:
        doc_obj = DocumentChecklist(**document.model_dump(),review_set_id=review_set.id)
        await doc_obj.insert()
        credit_response.documents_checklist.append(doc_obj)
    return credit_response

async def review_loan_application2(application: LoanApplication = Body(...)):
    # print(application)
    config = {
        "configurable": {
            "thread_id": application.id,
            "metadata": application.model_dump(),
        }
    }
    result = await CreditAgent.credit_agent(
        {
            "messages": [],  # Initialize with empty messages # Pass loan details directly
        },
        config=config,
    )
    review_set = ReviewSet(application_id=application.id)
    await review_set.insert()
    credit_response = CreditResponse(
        review_set=[],
        agent_lifecycle=[],
        documents_checklist=[]
    )
    for review in result.review_set:
        review_obj = Review(**review.model_dump(),review_set_id=review_set.id)
        await review_obj.insert()
        credit_response.review_set.append(review_obj)
    for agent in result.agent_lifecycle:
        agent_obj = AgentLifeCycle(**agent.model_dump(),review_set_id=review_set.id)
        await agent_obj.insert()
        credit_response.agent_lifecycle.append(agent_obj)
    for document in result.documents_checklist:
        doc_obj = DocumentChecklist(**document.model_dump(),review_set_id=review_set.id)
        await doc_obj.insert()
        credit_response.documents_checklist.append(doc_obj)
    return credit_response
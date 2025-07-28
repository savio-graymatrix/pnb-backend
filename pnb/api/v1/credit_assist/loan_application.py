from fastapi import (
    APIRouter,
    HTTPException,
    Body,
    Query,
    Depends,
    UploadFile,
    File as FastAPIFile,
    Form,
)
from fastapi.responses import HTMLResponse, Response
from typing import List, Optional
from pnb.db.data_models import (
    LoanApplication,
    UpdateLoanApplication,
    Review,
    ReviewSet,
    ReviewSetResponse,
    AgentLifeCycle,
    DocumentChecklist,
    LoanApplicationDocuments,
)
from pnb.db.utils import CursorPaginationRequest, CursorPaginationResponse
from datetime import datetime, timezone
from beanie.operators import Set
from pnb.langgraph.workflows import GRAPHS
from pnb.langgraph.agents.credit_agent import CreditAgent
from pnb import LOGGER
from pnb.langgraph.tools.extractor import store_text_embedding
from jinja2 import Template
from beanie import PydanticObjectId
from pnb.api.v1.file_upload import upload_files
import json
import traceback

router = APIRouter(prefix="/loan_application", tags=["Credit Assist · Loan Application"])

loan_form_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Loan Application Form</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f6f8;
            margin: 0;
            padding: 0;
        }

        .container {
            width: 600px;
            margin: 40px auto;
            background: #fff;
            padding: 30px 40px;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0,0,0,0.1);
        }

        h2 {
            text-align: center;
            color: #333;
        }

        h3 {
            margin-top: 30px;
            color: #444;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
        }

        label {
            display: block;
            margin-top: 15px;
            font-weight: bold;
            color: #333;
        }

        input[type="text"],
        input[type="number"],
        input[type="file"],
        select,
        textarea {
            width: 100%;
            padding: 10px;
            margin-top: 6px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 14px;
            box-sizing: border-box;
        }

        textarea {
            resize: vertical;
        }

        input[type="submit"] {
            margin-top: 25px;
            width: 100%;
            background-color: #007bff;
            color: white;
            padding: 12px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.2s ease-in-out;
        }

        input[type="submit"]:hover {
            background-color: #0056b3;
        }

        input[type="file"] {
            padding: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Loan Application Form</h2>
        <form action="/api/v1/loan_application/upload/create" method="post" enctype="multipart/form-data">
            <label>Applicant Name:</label>
            <input type="text" name="applicant_name" required>

            <label>PAN Number:</label>
            <input type="text" name="pan_no" required>

            <label>Aadhar Number:</label>
            <input type="text" name="aadhar_no" required>

            <label>GSTIN:</label>
            <input type="text" name="gstin" required>

            <label>Business Name:</label>
            <input type="text" name="business_name" required>

            <label>Business Type:</label>
            <input type="text" name="business_type" required>

            <label>Business Address:</label>
            <textarea name="business_address" required></textarea>

            <label>Loan Type:</label>
            <select name="loan_type" required>
                <option value="Retail">Retail</option>
                <option value="Business">Business</option>
            </select>

            <label>Loan Amount (₹):</label>
            <input type="number" name="loan_amount" step="0.01" min="0.01" required>

            <label>Loan Amount Applied (₹):</label>
            <input type="number" name="loan_amount_applied" step="0.01" min="0.01" required>

            <label>Monthly Turnover (₹):</label>
            <input type="number" name="monthly_turnover" step="0.01" min="0.01" required>

            <label>Net Profit (₹):</label>
            <input type="number" name="net_profit" step="0.01" min="0.01" required>

            <label>Established Year:</label>
            <input type="text" name="established_year" required>

            <label>Loan Tenure (months):</label>
            <input type="number" name="loan_tenure" min="1" required>

            <label>Interest Rate (%):</label>
            <input type="number" name="interest_rate" step="0.001" min="0.001" required>

            <h3>Documents</h3>

            <label>Aadhar Document (PDF/Image):</label>
            <input type="file" name="aadhar_document" accept=".pdf,.jpg,.jpeg,.png" required>

            <label>PAN Document (PDF/Image):</label>
            <input type="file" name="pan_document" accept=".pdf,.jpg,.jpeg,.png" required>

            <label>Loan Application Document (PDF/Image):</label>
            <input type="file" name="loan_application_document" accept=".pdf,.jpg,.jpeg,.png" required>

            <input type="submit" value="Submit Application">
        </form>
    </div>
</body>
</html>
"""


success_html = """
<!DOCTYPE html>
<html>
<head><title>Success</title></head>
<body>
    <h3>Loan application submitted successfully!</h3>
    <a href="/api/v1/loan_application/upload/apply">Return to previous page</a>
</body>
</html>
"""


@router.get("/upload/apply", response_class=HTMLResponse)
async def upload_page():
    return HTMLResponse(Template(loan_form_template).render())


@router.post("/upload/create")
async def handle_loan_application(
    applicant_name: str = Form(...),
    pan_no: str = Form(...),
    aadhar_no: str = Form(...),
    gstin: str = Form(...),
    business_name: str = Form(...),
    business_type: str = Form(...),
    business_address: str = Form(...),
    loan_type: str = Form(...),
    loan_amount: float = Form(...),
    loan_amount_applied: float = Form(...),
    monthly_turnover: float = Form(...),
    net_profit: float = Form(...),
    established_year: str = Form(...),
    loan_tenure: int = Form(...),
    interest_rate: float = Form(...),
    aadhar_document: UploadFile = FastAPIFile(...),
    pan_document: UploadFile = FastAPIFile(...),
    loan_application_document: UploadFile = FastAPIFile(...),
):
    try:
        file_response = await upload_files(
            [aadhar_document, pan_document, loan_application_document]
        )
        file_response = json.loads(file_response.body)['files']
        print(file_response)
        application_obj = await LoanApplication(
            applicant_name=applicant_name,
            pan_no=pan_no,
            aadhar_no=aadhar_no,
            gstin=gstin,
            business_name=business_name,
            business_type=business_type,
            business_address=business_address,
            loan_type=loan_type,
            loan_amount=loan_amount,
            loan_amount_applied=loan_amount_applied,
            monthly_turnover=monthly_turnover,
            net_profit=net_profit,
            established_year=established_year,
            loan_tenure=loan_tenure,
            interest_rate=interest_rate,
            documents=LoanApplicationDocuments(
                aadhar_document=file_response[0]["url"],
                pan_document=file_response[1]["url"],
                loan_application_document=file_response[2]["url"],
            ),
        ).insert()
        for document in application_obj.documents.model_dump().values():
            await store_text_embedding(application_obj.id, str(document))
        return HTMLResponse(success_html)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500,detail="Something went wrong")


# Create Loan Applications
@router.post("/")
async def create_application(applications: List[LoanApplication]):
    created_applications = list()
    for application in applications:
        application_obj = LoanApplication(**application.model_dump())
        await application_obj.insert()
        for document in application_obj.documents:
            await store_text_embedding(application_obj.id, str(document[1]))
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
    loan_application = await LoanApplication.get(PydanticObjectId(application_id))
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
    credit_response = ReviewSetResponse(
        review_set=[], agent_lifecycle=[], documents_checklist=[]
    )
    for review in result.review_set:
        review_obj = Review(**review.model_dump(), review_set_id=review_set.id)
        await review_obj.insert()
        credit_response.review_set.append(review_obj)
    for agent in result.agent_lifecycle:
        agent_obj = AgentLifeCycle(**agent.model_dump(), review_set_id=review_set.id)
        await agent_obj.insert()
        credit_response.agent_lifecycle.append(agent_obj)
    for document in result.documents_checklist:
        doc_obj = DocumentChecklist(
            **document.model_dump(), review_set_id=review_set.id
        )
        await doc_obj.insert()
        credit_response.documents_checklist.append(doc_obj)
    return credit_response

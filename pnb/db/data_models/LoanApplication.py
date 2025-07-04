from beanie import Document, PydanticObjectId
from typing import Optional, List
from pydantic import BaseModel


class LoanApplication(Document):
    applicant_name: str
    pan_no: str
    aadhar_no: str
    pan_document: PydanticObjectId
    aadhar_dcoument: PydanticObjectId

class UpdateLoanApplication(BaseModel):
    applicant_name: Optional[str]
    pan_no: Optional[str]
    aadhar_no: Optional[str]
    pan_document: Optional[PydanticObjectId]
    aadhar_dcoument: Optional[PydanticObjectId]
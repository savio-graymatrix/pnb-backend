from beanie import Document, PydanticObjectId
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator
from decimal import Decimal
from bson.decimal128 import Decimal128
from datetime import datetime, timezone

class LoanApplicationDocuments(BaseModel):
    aadhar_document: HttpUrl
    loan_application_document: HttpUrl
    pan_document:HttpUrl

class LoanApplication(Document):
    applicant_name: str
    pan_no: str
    aadhar_no: str
    gstin: str
    business_name: str
    business_type: str
    business_address: str
    loan_type: Literal["Retail","Business"]
    loan_amount: Decimal = Field(...,gt=0.0,decimal_places=2)
    loan_amount_applied: Decimal = Field(...,gt=0.0)
    monthly_turnover: Decimal = Field(...,gt=0.0,decimal_places=2)
    net_profit: Decimal = Field(...,gt=0.0,decimal_places=2)
    established_year: str
    loan_tenure: int
    interest_rate: Decimal = Field(...,gt=0.0,decimal_places=3)
    created_at: datetime = Field(default_factory=lambda : datetime.now().astimezone(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda : datetime.now().astimezone(timezone.utc))
    documents: LoanApplicationDocuments
    
    @field_validator(
        "loan_amount",
        "loan_amount_applied",
        "monthly_turnover",
        "net_profit",
        "interest_rate",
        mode="before"
    )
    
    @classmethod
    def convert_decimal128(cls, v):
        if isinstance(v, Decimal128):
            return v.to_decimal()
        return v


class UpdateLoanApplication(BaseModel):
    applicant_name: Optional[str]
    pan_no: Optional[str]
    aadhar_no: Optional[str]
    pan_document: Optional[PydanticObjectId]
    aadhar_document: Optional[PydanticObjectId]
    business_name: Optional[str]
    business_type: Optional[str]
    gstin: Optional[str]
    business_address: Optional[str]
    loan_type: Optional[Literal["Retail","Business"]]
    loan_amount: Optional[Decimal] = Field(...,gt=0.0,decimal_places=2)
    loan_amount_applied: Optional[Decimal] = Field(...,gt=0.0)
    monthly_turnover: Optional[Decimal] = Field(...,gt=0.0,decimal_places=2)
    net_profit: Optional[Decimal] = Field(...,gt=0.0,decimal_places=2)
    established_year: Optional[str]
    loan_tenure: Optional[int]
    interest_rate: Optional[Decimal] = Field(...,gt=0.0,decimal_places=3)
    created_at: Optional[datetime] = Field(default_factory=datetime.now().astimezone(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=datetime.now().astimezone(timezone.utc))
    gstin_document: Optional[PydanticObjectId]
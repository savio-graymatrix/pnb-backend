from beanie import Document, Link
from pydantic import Field, EmailStr, field_validator
from enum import Enum
from typing import List
from datetime import datetime, timezone
from .Customer import CustomerSegment


class ProductType(Enum):
    DEBIT_CARD = "Debit Card"
    CREDIT_CARD = "Credit Card"
    FIXED_DEPOSIT = "Fixed Deposit"
    PERSONAL_LOAN = "Personal Loan"
    HOME_LOAN = "Home Loan"


class Product(Document):
    name: str
    product_id: str
    type: ProductType
    recommended: List[Link[CustomerSegment]]
    description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

from beanie import Document, Link, before_event, after_event, Insert
from pydantic import Field
from enum import Enum
from typing import List
from datetime import datetime, timezone
from .Customer import CustomerSegment
import asyncio
from pnb.db.utils import handle_add_to_knowledge_graph, create_identifier


class ProductType(Enum):
    DEBIT_CARD = "Debit Card"
    CREDIT_CARD = "Credit Card"
    FIXED_DEPOSIT = "Fixed Deposit"
    PERSONAL_LOAN = "Personal Loan"
    HOME_LOAN = "Home Loan"
    SECURED_LOAN = "Secured Loan"
    LOAN = "Loan"
    GOLD_COIN = "Gold Coin"
    DEPOSIT = "Deposit"
    INSURANCE = "Insurance"


class Product(Document):
    name: str
    product_id: str
    type: ProductType
    recommended: List[Link[CustomerSegment]]
    description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "product"

    @before_event(Insert)
    async def handle_indentifier(self):
        await create_identifier(self)

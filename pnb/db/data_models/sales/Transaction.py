from beanie import Document, Link
from pydantic import Field
from typing import Optional
from .Customer import Customer
from datetime import datetime, timezone


class Transaction(Document):
    txn_id: str
    customer_id: str
    customer: Optional[Link[Customer]]
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    account_type: Optional[str] = None
    amount: Optional[float] = None
    channel: Optional[str] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
    balance_after: Optional[float] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "transaction"

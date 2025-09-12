from beanie import Document, Link
from pydantic import Field
from typing import Optional
from .Customer import Customer
from datetime import datetime


class Communication(Document):
    comm_id: str
    customer_id: str
    customer: Optional[Link[Customer]]
    date: datetime
    channel: str
    intent: Optional[str]
    message: Optional[str]
    bank_response: Optional[str]
    outcome: Optional[str]

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "communications"

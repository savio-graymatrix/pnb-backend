from beanie import Document, Link, after_event, Insert, before_event
from pydantic import Field, EmailStr, field_validator
from enum import Enum
import phonenumbers
from typing import Optional, List
from datetime import datetime, timezone
from pnb.db.utils import handle_add_to_knowledge_graph, create_identifier
import asyncio


class Customer(Document):
    customer_id: str = Field(..., description="Business-Facing ID")
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    occupation: Optional[str] = None
    income: Optional[float] = None
    segment: Optional[str] = None
    products_held: Optional[List[str]] = None
    credit_score: Optional[int] = None
    preferred_channel: Optional[str] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "customer"

    @before_event(Insert)
    async def handle_indentifier(self):
        await create_identifier(self)


# class Gender(Enum):
#     MALE = "Male"
#     FEMALE = "Female"
#     NOT_SPECIFIED = "Not Specified"


class CustomerSegment(Document):
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# class Customer(Document):
#     customer_id: str = None
#     name: str = None
#     age: int = Field(gt=0, le=200)
#     gender: Gender = Field()
#     email: EmailStr = Field()
#     phone_number: str
#     customer_segment: Link[CustomerSegment]

#     @field_validator("phone_number", mode="before")
#     def validate_phone(cls, value):
#         try:
#             parsed = phonenumbers.parse(
#                 value, None
#             )  # None = accept full international format
#             if not phonenumbers.is_valid_number(parsed):
#                 raise ValueError("Invalid phone number")
#             return phonenumbers.format_number(
#                 parsed, phonenumbers.PhoneNumberFormat.E164
#             )
#         except phonenumbers.NumberParseException:
#             raise ValueError("Invalid phone number format")

#     class Settings:
#         name = "customer"

#     @before_event(Insert)
#     async def handle_indentifier(self):
#         await create_identifier(self)

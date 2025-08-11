from beanie import Document, Link
from pydantic import Field, EmailStr, field_validator
from enum import Enum
import phonenumbers
from datetime import datetime, timezone


class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"
    NOT_SPECIFIED = "Not Specified"


class CustomerSegment(Document):
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Customer(Document):
    customer_id: str = None
    name: str = None
    age: int = Field(gt=0, le=200)
    gender: Gender = Field()
    email: EmailStr = Field()
    phone_number: str
    customer_segment: Link[CustomerSegment]

    @field_validator("phone", mode="before")
    def validate_phone(cls, value):
        try:
            parsed = phonenumbers.parse(
                value, None
            )  # None = accept full international format
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            return phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format")

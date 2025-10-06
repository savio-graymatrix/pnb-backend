from datetime import datetime, timezone
from typing import List, Literal
from beanie import Document, Link, Indexed, PydanticObjectId
from pydantic import BaseModel, Field


class CustomerInfo(Document):
    """Customer information document"""
    name: Indexed(str)
    phone_number: Indexed(str, unique=True)  # Unique phone numbers

    class Settings:
        name = "customer_info"


class Message(BaseModel):
    """Individual message within a transcript"""
    id: str
    type: Literal['transcript', 'suggestion']
    timestamp: datetime
    speaker: Literal['customer', 'agent', 'assistant']
    text: str


class Session(Document):
    """Session document containing customer info and transcripts"""
    session_id: Indexed(str, unique=True)
    customer_info: Link[CustomerInfo]  # Reference to CustomerInfo document
    transcript: List[Message] = Field(default_factory=list)

    call_time:                      datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    call_duration:                  str | None = None
    call_summary:                   str | None = None
    compliance:                     str | None = None
    score_card:                     str | None = None
    call_status:                    str | None = None
    call_score:                     int | None = None
    customer_satisfaction_score:    int | None = None
    call_improvement_suggestions:   str | None = None

    class Settings:
        name = "sessions"


class UpdateSession(BaseModel):
    session_id:                     str
    call_summary:                   str | None = None
    compliance:                     str | None = None
    score_card:                     str | None = None
    call_status:                    str | None = None
    call_score:                     int | None = None
    customer_satisfaction_score:    int | None = None
    call_improvement_suggestions:   str | None = None


class Notes(Document):
    """Notes document with customer info reference"""
    cust_info: Link[CustomerInfo]  # Reference to CustomerInfo document
    text: str
    timestamp: Indexed(datetime) = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "notes"

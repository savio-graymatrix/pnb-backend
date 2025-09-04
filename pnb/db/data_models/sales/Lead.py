from typing import Optional, List
from datetime import datetime, timezone
from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class LeadContact(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class LeadSource(Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    AD_CAMPAIGN = "ad_campaign"


class LeadStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    ACTIVE = "active"
    LOST = "lost"
    CONVERTED = "converted"


class Lead(Document):
    # Lead basic info
    name: str  # indexed for faster search
    company: Optional[str] = None
    title: Optional[str] = None

    # Contact details
    contact: Optional[LeadContact] = None

    # Lead details
    status: LeadStatus = "new"  # new, contacted, qualified, lost, converted
    source: LeadSource = None  # e.g. website, referral, ad campaign
    tags: Optional[List[str]] = []

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "lead"  # MongoDB collection name
        use_state_management = True  # track changes automatically

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "company": "Acme Corp",
                "title": "Procurement Manager",
                "contact": {
                    "email": "john.doe@example.com",
                    "phone": "+1-202-555-0182",
                    "address": "123 Business St, NY",
                },
                "status": "new",
                "source": "website",
                "tags": ["banking", "priority"],
            }
        }

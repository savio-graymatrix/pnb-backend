from beanie import Document
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from bson.decimal128 import Decimal128
from typing import Literal, List
from datetime import datetime, timezone
from pnb.db.data_models import File


class Tender(Document):
    title: str = Field(max_length=255)
    department: str = Field()
    type: str = Literal["open_tender", "limited_tender"]
    requirement: str = Field()
    budget: Decimal = Field(...,gt=0.0,decimal_places=2)
    mode_of_tender: Literal["online", "offline"] = Field()
    opening_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = Field(max_length=1024)
    documents: List[File] = Field(default=[])
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "tender"
    
    @field_validator(
        "budget",
        mode="before"
    )
    
    @classmethod
    def convert_decimal128(cls, v):
        if isinstance(v, Decimal128):
            return v.to_decimal()
        return v

class UpdateTender(BaseModel):
    department: str = Field()
    type: str = Literal["open_tender", "limited_tender"]
    requirement: str = Field()
    budget: Decimal = Field()
    mode_of_tender: Literal["online", "offline"] = Field()
    opening_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = Field(max_length=1024)
    documents: List[File] = Field(default=[])
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

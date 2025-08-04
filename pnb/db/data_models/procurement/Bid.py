from datetime import datetime, timezone
from pnb.db.data_models import File, Tender
from beanie import Document, Link, PydanticObjectId, before_event, Insert
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from typing import Optional
from enum import Enum
from pnb.db.utils import create_identifier
from bson.decimal128 import Decimal128


class EMDStatus(Enum):
    PAID = "paid"
    PENDING = "pending"
    NULL = "null"


class Bid(Document):
    series_id: Optional[str] = None
    company: str = Field()
    emd_status: Optional[EMDStatus] = Field(default=EMDStatus.PAID)
    amount: Optional[Decimal] = Field(default=0.0, gt=0.0, decimal_places=2)
    tender: Link[Tender] = Field()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    financials: File = Field()
    operationals: File = Field()
    technicals: File = Field()
    reasoning: Optional[str] = None
    score: Optional[int] = None
    pq: Optional[bool] = None
    tq: Optional[bool] = None

    class Settings:
        name = "bid"

    @before_event(Insert)
    async def assign_identifier(self):
        await create_identifier(self)

    @field_validator("amount", mode="before")
    @classmethod
    def convert_decimal128(cls, v):
        if isinstance(v, Decimal128):
            return v.to_decimal()
        return v


class UpdateBid(BaseModel):
    company: Optional[str]
    emd_status: Optional[EMDStatus] = Field(default=EMDStatus.NULL)
    amount: Optional[Decimal]
    tender: Optional[Link[Tender]]
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    financials: Optional[File]
    operationals: Optional[File]
    technicals: Optional[File]
    reasoning: Optional[str] = None
    score: Optional[int] = None
    pq: Optional[bool] = None
    tq: Optional[bool] = None


class CreateBid(BaseModel):
    company: str = Field()
    emd_status: Optional[EMDStatus] = Field(default=EMDStatus.NULL)
    amount: Optional[Decimal] = Field(..., gt=0.0, decimal_places=2)
    tender: PydanticObjectId = Field()

from datetime import datetime, timezone
from pnb.db.data_models import File, Tender
from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from enum import Enum

class EMDStatus(Enum):
    PAID = "paid"
    PENDING = "pending"
    NULL = "null"


class Bid(Document):
    company: str = Field()
    emd_status: EMDStatus = Field(default=EMDStatus.NULL)
    amount: Decimal = Field(...,gt=0.0,decimal_places=2)
    tender: Link[Tender] = Field()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    financials: File = Field()
    operationals: File = Field()
    technicals: File = Field()
    score: int = Field()
    pq: bool = Field()
    tq: bool = Field()
    
    class Settings:
        name = "bid"


class UpdateBid(BaseModel):
    company: Optional[str] = Field()
    emd_status: Optional[EMDStatus] = Field(default=EMDStatus.NULL)
    amount: Optional[Decimal] = Field(...,gt=0.0,decimal_places=2)
    tender: Optional[Link[Tender]] = Field()
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    financials: Optional[File] = Field()
    operationals: Optional[File] = Field()
    technicals: Optional[File] = Field()
    score: Optional[int] = Field()
    pq: Optional[bool] = Field()
    tq: Optional[bool] = Field()

class CreateBid(BaseModel):
    company: str = Field()
    emd_status: Optional[EMDStatus] = Field(default=EMDStatus.NULL)
    amount: Optional[Decimal] = Field(...,gt=0.0,decimal_places=2)
    tender: PydanticObjectId = Field()
   
    

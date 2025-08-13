from beanie import Document, before_event, Insert, after_event
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from bson.decimal128 import Decimal128
from typing import Literal, List, Optional
from datetime import datetime, timezone
from pnb.db.data_models import File
from enum import Enum
from pnb.db.utils import create_identifier, handle_add_to_knowledge_graph


class TenderDomain(str, Enum):
    GOODS = "Goods"
    SERVICES = "Services"
    WORKS = "Works"
    CONSULTANCY = "Consultancy"
    OTHERS = "Others"


class TenderStatus(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    LIVE = "Live"
    CORRINGENDUM = "Corrigendum"
    DRAFT = "Draft"


class TenderType(str, Enum):
    OPEN_TENDER = "Open Tender"
    LIMITED_TENDER = "Limited Tender"


class Tender(Document):
    series_id: Optional[str] = Field(default=None)
    title: str = Field(max_length=255)
    department: str = Field()
    type: TenderType = Field(default=TenderType.OPEN_TENDER)
    domain: TenderDomain = Field(default=TenderDomain.GOODS)
    requirement: str = Field()
    budget: Decimal = Field(..., gt=0.0, decimal_places=2)
    mode_of_tender: Literal["online", "offline"] = Field()

    description: str = Field(max_length=1024)
    emd: Decimal = Field(..., gt=0.0, decimal_places=2)
    officer: str = Field()
    opening_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closing_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: TenderStatus = Field(default=TenderStatus.DRAFT)
    documents: List[File] = Field(default=[])
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "tender"

    @before_event(Insert)
    async def handle_indentifier(self):
        await create_identifier(self)

    @after_event(Insert)
    async def add_to_knowledge_graph(data: Document):
        await handle_add_to_knowledge_graph(data)

    @field_validator("budget", "emd", mode="before")
    @classmethod
    def convert_decimal128(cls, v):
        if isinstance(v, Decimal128):
            return v.to_decimal()
        return v


class UpdateTender(BaseModel):
    department: str = Field()
    type: TenderType = Field(default=TenderType.OPEN_TENDER)
    requirement: str = Field()
    budget: Decimal = Field()
    mode_of_tender: Literal["online", "offline"] = Field()
    opening_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = Field(max_length=1024)
    documents: List[File] = Field(default=[])
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

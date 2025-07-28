from beanie import Document, before_event, Insert
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Literal, List
from datetime import datetime, timezone
from pnb.db.utils.events import create_identifier
from pnb.db.data_models import File


class Tender(Document):
    title: str = Field(max_length=255)
    department: str = Field()
    type: str = Literal["open_tender", "limited_tender"]
    requirement: str = Field()
    budget: Decimal = Field()
    mode_of_tender: Literal["online", "offline"] = Field()
    opening_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = Field(max_length=1024)
    documents: List[File] = Field(default=[])
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @before_event(Insert)
    async def generate_id(self):
        return await create_identifier(self)

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

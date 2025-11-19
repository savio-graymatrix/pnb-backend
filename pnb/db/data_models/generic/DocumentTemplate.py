from tempfile import template
from beanie import Document, Link, PydanticObjectId, before_event, Insert, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import Field, BaseModel
from datetime import datetime, timezone
from typing import Optional
from pnb.db.utils import create_identifier
from pnb.core.settings import SETTINGS
from enum import Enum


class DocumentType(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    PDF = "pdf"


class DocumentTemplate(Document):
    series_id: str = Field(default=None)
    name: str = Field(max_length=255)
    type: DocumentType = Field()
    template: str = Field()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "document_template"

    @before_event(Insert)
    async def handle_indentifier(self):
        await create_identifier(self)

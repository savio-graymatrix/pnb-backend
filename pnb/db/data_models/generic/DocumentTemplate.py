from beanie import Document, Link, PydanticObjectId, before_event, Insert
from pydantic import Field, BaseModel
from datetime import datetime, timezone
from typing import Optional
from pnb.db.utils import create_identifier


class DocumentTemplate(Document):
    series_id : str = Field(default=None)
    name: str = Field(max_length=255)
    template: str = Field()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "document_template"
    
    @before_event(Insert)
    async def handle_indentifier(self):
        await create_identifier(self)
from beanie import Document, before_event, Insert, Link
from pydantic import Field
from datetime import datetime, timezone
from pnb.db.utils.events import create_identifier
from pnb.db.data_models import Tender
from typing import Optional

class Query(Document):
    question: str
    response: str
    company: str
    tender: Link[Tender]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    @before_event(Insert)
    async def generate_id(self):
        return await create_identifier(self)

class UpdateQuery(Query):
    question: Optional[str]
    response: Optional[str]
    company: Optional[str]
    tender: Link[Tender]
    # created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))



from beanie import Document, Link
from pydantic import Field
from datetime import datetime, timezone
from pnb.db.data_models import Tender
from typing import Optional

class Query(Document):
    question: str
    response: str
    company: str
    tender: Link[Tender]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "query"
    

class UpdateQuery(Query):
    question: Optional[str]
    response: Optional[str]
    company: Optional[str]
    tender: Link[Tender]
    # created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))



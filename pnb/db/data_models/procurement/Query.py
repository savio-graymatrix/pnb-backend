from beanie import Document, Link, PydanticObjectId, before_event, Insert
from pydantic import Field, BaseModel
from datetime import datetime, timezone
from pnb.db.data_models import Tender
from typing import Optional
from pnb.db.utils import create_identifier


class Query(Document):
    series_id: Optional[str] = Field()
    question: str
    response: Optional[str]
    company: str
    tender: Link[Tender]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "query"

    @before_event(Insert)
    async def assign_identifier(self):
        await create_identifier(self)


class UpdateQuery(Query):
    question: Optional[str]
    response: Optional[str]
    company: Optional[str]
    tender: PydanticObjectId
    # created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class QueryStructuredOutput(BaseModel):
    answer: str = Field(
        description="Previous Response given by the agent for the query. Do not create your response to it"
    )

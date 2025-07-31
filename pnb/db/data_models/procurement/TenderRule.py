from beanie import Document, Link, before_event, Insert
from pydantic import Field, BaseModel
from datetime import datetime, timezone
from pnb.db.data_models import Tender
from typing import Optional
from typing import List
from pnb.db.utils import create_identifier

class TenderRule(Document):
    series_id: Optional[str] = None 
    content: str = Field()
    tender: Link[Tender]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "tender_rule"
    
    @before_event(Insert)
    async def assign_identifier(self):
        await create_identifier(self)

class UpdateTenderRule(TenderRule):
    content: Optional[str] = Field()
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

class TenderRuleSetStructuredOutput(BaseModel):
    rules : List[str] = Field(description="List of Rules")

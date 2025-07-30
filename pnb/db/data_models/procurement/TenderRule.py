from beanie import Document, Link
from pydantic import Field, BaseModel
from datetime import datetime, timezone
from pnb.db.data_models import Tender
from typing import Optional
from typing import List

class TenderRule(Document):
    content: str = Field()
    tender: Link[Tender]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "tender_rule"

class UpdateTenderRule(TenderRule):
    content: Optional[str] = Field()
    # created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

class TenderRuleSetStructuredOutput(BaseModel):
    rules : List[str] = Field(description="List of Rules")

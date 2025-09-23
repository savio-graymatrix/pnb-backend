from pydantic import Field, BaseModel, ConfigDict
from typing import Literal
from datetime import datetime, timezone


class SummarizedTranscript(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})
    summary: str = Field(description="A summary of the Transcript")
    sentiment: Literal["positive", "negative", "mixed", "neutral"] = Field(
        description="General sentiment of the whole call"
    )
    next_action: str = Field(description="Next action according to the summary")
    next_action_date: str | None = Field(
        description="Date when will be the next action will be taken. Date is in ISO format in UTC Timezone."
    )

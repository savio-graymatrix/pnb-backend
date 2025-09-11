from pydantic import Field, BaseModel
from typing import Literal


class SummarizedTranscript(BaseModel):
    summary: str = Field(description="A summary of the Transcript")
    sentiment: Literal["positive", "negative", "mixed", "neutral"] = Field(
        description="General sentiment of the whole call"
    )
    next_action: str = Field(description="Next action according to the summary")

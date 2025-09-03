from pydantic import Field, BaseModel


class SummarizedTranscript(BaseModel):
    summary: str = Field(description="A summary of the Transcript")
    next_action: str = Field(description="Next action according to the summary")

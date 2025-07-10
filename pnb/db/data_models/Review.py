from beanie import Document, PydanticObjectId, before_event, Save
from typing import Optional, Literal, List
from pydantic import Field, BaseModel
from datetime import datetime, timezone


REVIEW_STATUSES = ["resolved", "rejected"]


class Review(Document):
    alert: str = None
    title: str = None
    message: str = None
    review_set_id: PydanticObjectId
    review_comment: Optional[str] = None
    review_status: Literal["pending", "resolved", "rejected"] = "pending"
    updated_at: datetime = Field(default_factory=lambda : datetime.now().astimezone(timezone.utc))
    created_at: datetime = Field(default_factory=lambda : datetime.now().astimezone(timezone.utc))
    @before_event(Save)
    async def prevent_status_change(self):
        if self.id is not None:
            current = await Review.get(self.id)
            if (
                current
                and current.status != "pending"
                or self.status not in REVIEW_STATUSES
            ):
                raise ValueError(
                    f"Cannot change status from final state: {current.status}"
                )

    @before_event(Save)
    async def restrict_comment_changes(self):
        if self.id is not None:
            current = await Review.get(self.id)
            if (
                current.review_comment is not None
                and self.review_comment is not None
                and self.review_status in REVIEW_STATUSES
            ):
                raise ValueError(f"Cannot update comment once resolved or rejected")


class ReviewSet(Document):
    application_id: PydanticObjectId
    updated_at: datetime = Field(default_factory=lambda : datetime.now().astimezone(timezone.utc))
    created_at: datetime = Field(default_factory=lambda : datetime.now().astimezone(timezone.utc))


class UpdateReview(Review):
    alert: Optional[str] = None
    title: Optional[str] = None
    message: Optional[str] = None
    review_comment: Optional[str] = None
    review_status: Optional[Literal["pending", "resolved", "rejected"]] = None
    review_set_id: Optional[PydanticObjectId] = None

    class Config:
        extra = "forbid"

class ReviewSetResponse(ReviewSet):
    reviews: List[Review]

class AgentLifeCycle(Document):
    review_set_id : PydanticObjectId = Field(description="Parent Review Set ID")
    agent_name: str = Field(description="The name of the agent. Please append 'agent' tag to the names and humanise it")
    reasoning: str = Field(description="The action performed by the agent for their tasks")

class DocumentChecklist(Document):
    review_set_id : PydanticObjectId = Field(description="Parent Review Set ID")
    document_name: str
    file_url : str
    isVerified : bool

class CreditResponse(BaseModel):
    review_set: List[Review] = Field(description="The review set in as in the response by the 'credit_assist_agent'")
    agent_lifecycle: List[AgentLifeCycle] = Field(default=[])
    documents_checklist: List[DocumentChecklist] = Field(default=[])

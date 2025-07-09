from beanie import Document, PydanticObjectId, before_event, Save
from typing import Optional, Literal, List


REVIEW_STATUSES = ["resolved","rejected"]

class Review(Document):
    alert: str
    title: str
    message: str
    review_set_id: PydanticObjectId
    review_comment: str
    review_status: Literal["pending","resolved","rejected"] = "pending"
    
    @before_event(Save)
    async def prevent_status_change(self):
        if self.id is not None:  
            current = await Review.get(self.id)
            if current and current.status != "pending" or self.status not in REVIEW_STATUSES:
                raise ValueError(f"Cannot change status from final state: {current.status}")
    
    @before_event(Save)
    async def restrict_comment_changes(self):
        if self.id is not None:
            if self.review_comment and self.review_status in REVIEW_STATUSES:
                raise ValueError(f"Cannot update comment once resolved or rejected")
            

class ReviewSet(Document):
    application_id: PydanticObjectId

class UpdateReview(Review):
    action: Optional[str]
    title: Optional[str]
    review_set_id: Optional[PydanticObjectId]

class ReviewSetResponse(ReviewSet):
    reviews: List[Review]




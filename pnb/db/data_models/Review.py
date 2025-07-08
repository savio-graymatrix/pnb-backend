from beanie import Document, PydanticObjectId
from typing import Optional, Literal, List


class ReviewPoints(Document):
    status: Literal["positive","caution","negative"]
    statement: str

class Review(Document):
    alert: str
    title: str
    message: str
    review_points: List[ReviewPoints]
    review_set_id: PydanticObjectId
    review_comment: str
    review_status: Literal["pending","resolved","issue"]

class ReviewSet(Document):
    application_id: PydanticObjectId

class UpdateReview(Review):
    action: Optional[str]
    title: Optional[str]
    review_points: Optional[List[ReviewPoints]]
    review_set_id: Optional[PydanticObjectId]

class ReviewSetResponse(ReviewSet):
    reviews: List[Review]




from langchain_core.tools import tool
from pnb.db.data_models import Review, UpdateReview
from fastapi import HTTPException, status
from beanie.operators import Set
from datetime import datetime, timezone
import json
from beanie import PydanticObjectId
from pydantic import ValidationError
from typing import Literal

@tool
async def patch_review_tool(review_id: str, review_status: Literal["resolved", "rejected"]) -> dict:
    """
    Updates the status of a review in the database to either 'resolved' or 'rejected'.
    
    Args:
    review_id (str): The ID of the review to update.
    review_status (Literal["resolved", "rejected"]): The status to set for the review.
    
    Returns:
    dict: A dictionary containing the updated review.

    Raises:
    ValueError: If the review_id is invalid.
    HTTPException: If the review is not found in the database (status code 404).

    """
    # Validate and convert review_id to PydanticObjectId
    try:
        review_id_obj = PydanticObjectId(review_id)
    except Exception as e:
        raise ValueError(f"Invalid review_id: {str(e)}")

    # Fetch the review from the database
    review = await Review.get(review_id_obj)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Update the review's status and timestamp
    update_data = {"review_status": review_status}
    review.updated_at = datetime.now(timezone.utc)

    # Apply the update to the database
    await review.update(Set(update_data))

    # Return the updated review as a dictionary
    return review
    
 
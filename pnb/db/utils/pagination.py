from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional
from datetime import datetime
from uuid import UUID
from beanie import PydanticObjectId

T = TypeVar("T")

class CursorPaginationRequest(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)
    after_id: Optional[PydanticObjectId] = Field(default=None, description="Fetch items after this ID")
    sort_by: Optional[str] = Field(default="created_at")
    sort_order: Optional[int] = Field(default=-1, description="1 for ascending, -1 for descending")

class CursorPaginationResponse(BaseModel, Generic[T]):
    items: List[T]
    next_cursor: Optional[PydanticObjectId] = None
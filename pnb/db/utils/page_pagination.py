from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")


class PagePaginationRequest(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number starting from 1")
    page_size: int = Field(
        default=10, ge=1, le=100, description="Number of items per page"
    )
    sort_by: Optional[str] = Field(default="created_at")
    sort_order: Optional[int] = Field(
        default=-1, description="1 for ascending, -1 for descending"
    )


class PagePaginationMetadata(BaseModel):
    currentPage: int
    itemsPerPage: int
    totalItems: int
    totalPages: int
    hasNextPage: bool
    hasPreviousPage: bool


class PagePaginationResponse(BaseModel, Generic[T]):
    items: List[T]
    pagination: PagePaginationMetadata

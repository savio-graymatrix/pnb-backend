from beanie import Document, Link, PydanticObjectId
from pydantic import HttpUrl, Field, BaseModel
from typing import Optional, List
from datetime import datetime, timezone


class ExtractedDocumentMetadata(BaseModel):
    filename: str
    filetype: str
    chunk_index: int
    hash: str
    tags: List[str]

class ExtractedDocument(Document):
    name: str = Field(..., description="Original name of the file")
    link_to: PydanticObjectId
    content: str = Field()
    metadata: ExtractedDocumentMetadata
    created_at: str = Field(
        default_factory=datetime.now().astimezone(timezone.utc).isoformat
    )

    class Settings:
        name = "extracted_document"
        
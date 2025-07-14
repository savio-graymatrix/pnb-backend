from beanie import Document
from pydantic import HttpUrl, Field, ConfigDict, BaseModel
from typing import Optional, List
from datetime import datetime, timezone


class File(Document):
    name: str = Field(..., description="Original name of the file")
    url: HttpUrl = Field(..., description="Publicly accessible URL to the file")
    content_type: Optional[str] = Field(
        None, description="MIME type of the file, e.g., image/png"
    )
    size: Optional[int] = Field(None, description="Size of the file in bytes")
    uploaded_at: str = Field(
        default_factory=datetime.now().astimezone(timezone.utc).isoformat
    )

    class Settings:
        name = "file"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "profile_picture.png",
                "url": "https://cdn.example.com/uploads/profile_picture.png",
                "content_type": "image/png",
                "size": 204800,
                "uploaded_at": "2025-06-29T14:30:00Z",
            }
        },
    )
    
class UploadFileResponse(BaseModel):
    files: List[File]

class FileException(BaseModel):
    exception: str
    file: str

class UploadFileExceptionResponse(BaseModel):
    errors: List[FileException]
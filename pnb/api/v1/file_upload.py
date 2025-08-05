from fastapi import APIRouter, Query, UploadFile, File as FastAPIFile, HTTPException
from fastapi.responses import Response
from typing import Union, List
from pnb.db.data_models import (
    File,
    FileException,
    UploadFileExceptionResponse,
    UploadFileResponse,
)
from pnb.services.generic.upload_to_s3 import upload_to_s3
from uuid import uuid4

ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "application/pdf"}
MAX_FILE_SIZE = 20 * 1024 * 1024

router = APIRouter(prefix="/upload", tags=["File Upload"])


@router.post("/")
async def upload_files(files: List[UploadFile] = FastAPIFile(...)):
    exceptions = []
    for file in files:
        content = await file.read()
        await file.seek(0)
        if file.content_type not in ALLOWED_MIME_TYPES:
            exceptions.append(
                FileException(file=file.filename, exception="Unsupported file type")
            )

        if len(content) > MAX_FILE_SIZE:
            exceptions.append(
                FileException(
                    file=file.filename,
                    exception=f"File too Large. Please upload file with size less than {MAX_FILE_SIZE} bytes",
                )
            )

    if exceptions:
        return UploadFileExceptionResponse(errors=exceptions)
    uploaded_files = []
    for upload_file in files:
        upload_content = await upload_file.read()
        await upload_file.seek(0)
        ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid4().hex}.{ext}"

        try:
            public_url = upload_to_s3(upload_content, unique_filename, upload_file.content_type)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        file_doc = File(
            name=upload_file.filename,
            url=public_url,
            content_type=upload_file.content_type,
            size=len(upload_content),
        )
        await file_doc.insert()
        uploaded_files.append(file_doc)

    return Response(UploadFileResponse(files=uploaded_files).model_dump_json(), status_code=201)

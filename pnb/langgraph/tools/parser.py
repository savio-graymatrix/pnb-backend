import pymupdf4llm
from pnb.services.upload_to_s3 import s3_client
import fitz
from pnb import SETTINGS
from langchain_core.tools import tool





@tool
def extract_from_pdf(file_url: str):
    """Tool to extract pdf and parse into markdown"""
    # fill in your credentials to access the cloud
    response = s3_client.get_object(Bucket=SETTINGS.AWS_BUCKET, Key=file_url.split("/")[-1])
    mime = response["ContentType"]
    body = response["Body"]
    doc = fitz.open(mime, body.read())
    response = pymupdf4llm.to_markdown(doc)
    return response
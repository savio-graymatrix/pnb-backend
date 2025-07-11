from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions, TableFormerMode, TableStructureOptions, smolvlm_picture_description
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import _DocumentConversionInput
import boto3
import requests
import tempfile
import os
import logging
from langchain_core.tools import tool

_log = logging.getLogger(__name__)

image_prompt = """Your task is to extract data and insights from any embedded images, charts or diagrams in the PDF.Please do the following:
1. Analyze any **charts or diagrams** in the document (even those that may be image-based but appear in OCR text).
2. If the image contains fields such as names, addresses, PAN, aadhar, etc. extract it very accurately.
3. If the image contains any loan related information, extract it in **structured** format with appropriate keys and values.
4. If the image contains **tabular data**, extract it in **structured** format with appropriate keys and values.
5. If the image is a **chart or diagram**, summarize it by describing:
- What the chart shows
- Axis labels, units, values, trends, and comparisons
6. If specific numerical values are visible, extract it very accurately.
7. Keep the explanation complete.
**IMPORTANT**: Since your extracted content is going to be used for loan analysis, make sure you extract the data properly and accurately.
"""

@tool
def extract_from_docling(file_url: str) -> str:
    """Tool to extract text from a PDF or image using Docling OCR and return it as markdown."""
    source = file_url
    converter = DocumentConverter()
    result = converter.convert(source).document
    return result.export_to_text()
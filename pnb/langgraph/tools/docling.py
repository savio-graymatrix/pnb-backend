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
# def extract_with_docling(file_url: str) -> str:
    """Tool to extract text from a PDF or image using Docling OCR and return it as markdown.
    Args:
        file_url (str): URL to the PDF or image file (e.g., S3 URL or HTTP URL).
    Returns:
        str: Extracted content.
    """
    # Initialize S3 client
    s3_client = boto3.client("s3")

    # Determine if the URL is an S3 URL or HTTP URL
    is_s3_url = file_url.startswith("s3://")
    
    # Download the file
    try:
        if is_s3_url:
            # Extract bucket and key from S3 URL
            bucket = file_url.split("/")[2]
            key = "/".join(file_url.split("/")[3:])
            response = s3_client.get_object(Bucket=bucket, Key=key)
            file_content = response["Body"].read()
            mime_type = response["ContentType"]
        else:
            # Assume HTTP URL
            response = requests.get(file_url, stream=True)
            response.raise_for_status()
            file_content = response.content
            mime_type = response.headers.get("Content-Type", "")

        # Write content to a temporary file
        suffix = ".pdf" if "pdf" in mime_type.lower() else ".png"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name

        # Configure Docling pipeline
        easyocr_options = EasyOcrOptions(lang=["hi", "en"])
        table_structure_options = TableStructureOptions(mode=TableFormerMode.ACCURATE)
        picture_description_options = smolvlm_picture_description
        picture_description_options.prompt = image_prompt
        
        pipeline_options = PdfPipelineOptions(
            do_ocr=True,
            force_full_page_ocr=True,
            ocr_options=easyocr_options,
            do_table_structure=True,
            table_structure_options=table_structure_options,
            do_picture_description=True,
            picture_description_options=picture_description_options
        )
        
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        # Convert the document
        # doc_input = _DocumentConversionInput(path_or_stream_iterator=tmp_file_path)
        converted_doc = converter.convert(source=tmp_file_path).document

        # Export to markdown
        markdown_content = converted_doc.export_to_text()

        # Clean up temporary file
        os.unlink(tmp_file_path)

        return markdown_content

    except Exception as e:
        _log.error(f"Docling: Error processing document: {str(e)}")
        return f"Error processing document: {str(e)}"


print(extract_from_docling("https://ssm-talkk-dev.pocs.tech/3b9fefd95c2b46c09f60c285dd76b217.pdf"))
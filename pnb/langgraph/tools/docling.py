from docling.document_converter import DocumentConverter
from docling.datamodel.document import _DocumentConversionInput
import boto3
import requests
from io import BytesIO
import tempfile
import os
from langchain_core.tools import tool # Assuming the same framework as the provided example

@tool
def extract_with_docling(file_url: str) -> str:
    """
    Tool to extract text from a PDF or image using Docling OCR and return it as markdown.
    Args:
        file_url (str): URL to the PDF or image file (e.g., S3 URL or HTTP URL).
    Returns:
        str: Extracted content in markdown format.
    """
    # Initialize S3 client (assuming AWS credentials are configured)
    #s3_client = boto3.client("s3")

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
            response.raise_for_status()  # Raise exception for bad status codes
            file_content = response.content
            mime_type = response.headers.get("Content-Type", "")

        # Write content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf" if "pdf" in mime_type else ".png") as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name

        # Initialize Docling DocumentConverter
        converter = DocumentConverter()

        # Convert the document using Docling
        doc_input = _DocumentConversionInput(path=tmp_file_path)
        result = converter.convert_single(doc_input)

        # Extract text and structure it as markdown
        markdown_output = _convert_to_markdown(result)

        # Clean up temporary file
        os.unlink(tmp_file_path)

        return markdown_output

    except Exception as e:
        return f"Error processing document: {str(e)}"

def _convert_to_markdown(doc_result) -> str:
    """
    Convert Docling's document result to markdown format, optimized for loan application documents.
    Args:
        doc_result: The result object from Docling's document conversion.
    Returns:
        str: Markdown-formatted text.
    """
    markdown = []
    
    # Extract key fields relevant to loan applications
    if hasattr(doc_result, "main_text"):
        for element in doc_result.main_text:
            # Handle text blocks
            if element.type == "text":
                markdown.append(element.text)
            # Handle tables (common in loan documents for financial data)
            elif element.type == "table":
                markdown.append(_table_to_markdown(element))
            # Handle key-value pairs (e.g., Applicant Name: John Doe)
            elif element.type == "key_value":
                markdown.append(f"**{element.key}**: {element.value}")

    # Join all markdown elements with newlines
    return "\n\n".join(markdown)

def _table_to_markdown(table) -> str:
    """
    Convert a Docling table object to markdown table format.
    Args:
        table: Docling table object.
    Returns:
        str: Markdown table.
    """
    markdown = []
    headers = table.headers if hasattr(table, "headers") else []
    rows = table.rows if hasattr(table, "rows") else []

    if headers:
        markdown.append("| " + " | ".join(headers) + " |")
        markdown.append("| " + " | ".join(["---"] * len(headers)) + " |")
    
    for row in rows:
        markdown.append("| " + " | ".join(str(cell) for cell in row) + " |")
    
    return "\n".join(markdown)


print(extract_with_docling("https://ssm-talkk-dev.pocs.tech/3b9fefd95c2b46c09f60c285dd76b217.pdf"))
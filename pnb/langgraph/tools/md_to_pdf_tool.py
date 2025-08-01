from langchain_core.tools import tool
import markdown
import pdfkit
import uuid
from pnb.services.generic.upload_to_s3 import upload_to_s3
from botocore.exceptions import ClientError
from pnb.core.settings import SETTINGS

@tool
async def md_to_pdf_tool(markdown_text: str) -> str:
    """
    Converts markdown text to a PDF using Python-Markdown and wkhtmltopdf (via pdfkit), then uploads it to S3, returning the S3 URL.

    Args:
        markdown_text (str): The markdown text to convert to PDF (e.g., a report with headings, lists, and tables).

    Returns:
        str: The S3 URL of the uploaded PDF file.

    Raises:
        ValueError: If the markdown_text is empty or invalid.
        RuntimeError: If the PDF generation or S3 upload fails.
    """
    if not markdown_text or not isinstance(markdown_text, str):
        raise ValueError("Markdown text must be a non-empty string")

    try:
        # Setting up wkhtmltopdf configuration
        path_to_wkhtmltopdf = SETTINGS.WKHTML_PATH
        config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

        # Converting markdown to HTML with tables extension
        md = markdown.Markdown(extensions=['tables'])
        html_content = md.convert(markdown_text)

        # Defining HTML template with CSS
        css = """
        <style>
            body { font-family: Arial, sans-serif; margin: 1in; }
            h1, h2 { text-align: center; }
            table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            ul { margin: 10px 0; padding-left: 20px; }
            li { margin-bottom: 5px; }
        </style>
        """
        html_template = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Credit Appraisal Memorandum Report</title>
            {css}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # Converting HTML to PDF
        options = {
            'page-size': 'A4',
            'margin-top': '1in',
            'margin-right': '1in',
            'margin-bottom': '1in',
            'margin-left': '1in',
            'encoding': 'UTF-8',
            'quiet': ''
        }
        pdf_bytes = pdfkit.from_string(html_template, False, options=options, configuration=config)

        # Generating unique filename
        filename = f"reports/cam_report_{uuid.uuid4()}.pdf"

        # Uploading to S3
        s3_url = upload_to_s3(
            file_bytes=pdf_bytes,
            filename=filename,
            content_type="application/pdf"
        )

        return s3_url

    except Exception as e:
        raise RuntimeError(f"Failed to generate or upload PDF: {str(e)}")
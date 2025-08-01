from langchain_core.tools import tool
import markdown
import pdfkit
import uuid
from pnb.services.generic.upload_to_s3 import upload_to_s3
from botocore.exceptions import ClientError
from pnb.core.settings import SETTINGS
from jinja2 import Template, Environment
from pnb.db.data_models.generic.DocumentTemplate import DocumentTemplate
import markupsafe
from datetime import datetime


def nl2br(value: str) -> str:
    """
    Convert newline characters to HTML <br> tags, escaping the input for safety.
    
    Args:
        value (str): The input string to process.
    
    Returns:
        str: The string with newlines replaced by <br> tags, marked as safe HTML.
    """
    if not isinstance(value, str):
        return ""
    escaped = markupsafe.escape(value)
    return markupsafe.Markup(escaped.replace('\n', '<br>'))

def format_currency(value) -> str:
    """
    Format a number as USD currency (e.g., $500,000.00).
    
    Args:
        value: The input number (str, int, float, or Decimal).
    
    Returns:
        str: Formatted currency string or original value if invalid.
    """
    if value is None:
        return "N/A"
    try:
        # Handle string or number input (e.g., "500000" or 500000)
        num = float(value)
        return f"${num:,.2f}"
    except (ValueError, TypeError):
        return str(value)

def format_date(value) -> str:
    """
    Format an ISO 8601 date string to a readable format (e.g., August 01, 2025).
    
    Args:
        value: The input date string (ISO 8601 format).
    
    Returns:
        str: Formatted date string or original value if invalid.
    """
    if value is None:
        return "N/A"
    try:
        # Handle ISO 8601 date strings (e.g., "2025-08-01T00:00:00.000Z")
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y")
    except (ValueError, TypeError):
        return str(value)

@tool
async def template_to_pdf(name:str, context: dict):
    """
    Fetches a Jinja2 template from MongoDB, renders it with the provided python dictionary, converts it to a PDF using wkhtmltopdf (via pdfkit),
    and uploads it to S3, returning the S3 URL.

    Args:
        template_id (str): The name of the Jinja2 template to use. (Query Document, Tender Document, Bid Evaluation Report)
        context (dict): The dictionary containing data to render the template (e.g., bidder_name, analysis).
        This is how a sample bid evaluation context looks like:
        evaluation_context = {
            'bidder_name': 'KRS & SJ INFRASTRUCTURE',
            'tender_title': 'Construction of City Gate Station...',
            'crfq_no': '1000427710',
            'tender_id': '18849',
            'analysis': {
                'pq': {
                    'experience': 'Completion certificates provided...',
                    'statutory': 'GST, PAN documents are valid...',
                    'personnel': 'Key personnel CVs included...',
                    'status': 'PASS' # or 'FAIL'
                },
                'tq': {
                    'proposal': 'Detailed engineering methodology covers all scope...',
                    'certificates': 'Multiple completion certificates attached...',
                    'quality_safety': 'ISO 9001:2015 cert provided...',
                    'status': 'PASS'
                },
                'financial': {
                    'strength': 'Audited financial statements for FY 2021-24 provided...',
                    'emd_status': 'EMD status is not confirmed in the bid metadata. This is a critical issue.'
                },
                'compliance_rules': [
                    'Two-bid system: Documents are separated as required.',
                    'Online submission: Confirmed.',
                    'EMD: Not confirmed in the bid metadata (critical).'
                ]
            },
            'scoring': {
                'max_total_score': 100,
                'final_score': 88,
                'total_comment': 'Deduction only for EMD and minor financial comfort.',
                'criteria': [
                    {'name': 'Similar Work Experience', 'max_marks': 20, 'awarded_marks': 20, 'comment': 'Large, recent, relevant CGD project completed'},
                    # ... more criteria dictionaries
                ]
            },
            'summary': {
                'critical_notes': 'The only major compliance gap is the EMD status...',
                'recommendations': [
                    'If EMD is confirmed/rectified: The bid is compliant...',
                    'If EMD is not submitted: The bid is non-compliant...'
                ],
                'overall_compliance': 'Conditional'
            }
        }

    Returns:
        str: The S3 URL of the uploaded PDF file.

    Raises:
        ValueError: If template_id is empty or context is not a valid dictionary.
        RuntimeError: If template fetching, rendering, PDF generation, or S3 upload fails.
    """

    if not name or not context:
        raise ValueError("template_id and context must be provided")
    if name not in ["Query Document", "Tender Document", "Bid Evaluation Report"]:
        raise ValueError("Invalid template name")
    
    template = await DocumentTemplate.find_one(DocumentTemplate.name==name)
    if not template:
        raise ValueError("Template not found")
    
    template_content = template.template

    # Create Jinja2 environment with custom filters
    env = Environment()
    env.filters['nl2br'] = nl2br
    env.filters['format_currency'] = format_currency
    env.filters['format_date'] = format_date

    jinja_template = env.from_string(template_content)
    rendered = jinja_template.render(**context)

    path_to_wkhtmltopdf = SETTINGS.WKHTML_PATH
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
    options = {
        'page-size': 'A4',
        'margin-top': '1in',
        'margin-right': '1in',
        'margin-bottom': '1in',
        'margin-left': '1in',
        'encoding': 'UTF-8',
        'quiet': ''
    }
    pdf_bytes = pdfkit.from_string(rendered, False, options=options, configuration=config)
    filename = f"reports/{uuid.uuid4()}.pdf"

    s3_url = upload_to_s3(
        file_bytes=pdf_bytes,
        filename=filename,
        content_type="application/pdf"
    )
    return s3_url
    
    
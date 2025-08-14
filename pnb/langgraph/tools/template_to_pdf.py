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
    return markupsafe.Markup(escaped.replace("\n", "<br>"))


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
async def template_to_pdf(name: str, context: dict):
    """
    Fetches a Jinja2 template from MongoDB, renders it with the provided python dictionary, converts it to a PDF using wkhtmltopdf (via pdfkit),
    and uploads it to S3, returning the S3 URL.

    Args:
        `name`: The name of the Jinja2 template to use. (BPCL Query Document, BPCL Tender Document, BPCL Bid Evaluation Report)
        `context`: The dictionary containing data to render the template.
        This is a mock Query Document argument:
        {'name': 'BPCL Query Document', 'context': {'queries': [{'id': '688ca73debbeb712595f830e', 'company': 'Pacific Engineers', 'question': 'yo can you tell me about the tebder?', 'response': 'The tender is for the construction of a City Gate Station and Mother Station for a CGD project beside Goa. Budget: INR 600 million. EMD: INR 600,000. Submission is offline before 19-Dec-2025. Tender Document: https://ssm-talkk-dev.pocs.tech/reports/e160a234-43d3-4cda-b8e0-5487c0d45c2e.pdf', 'created_at': '2025-08-01 11:38:37'}, {'id': '688ca7a2ebbeb712595f830f', 'company': 'Pacific Engineers', 'question': 'wjere is the tender locstion?', 'response': 'The tender location is beside Goa.', 'created_at': '2025-08-01 11:40:18'}, {'id': '688ccfa4c234cae92002cde0', 'company': 'gRAY mATRIX', 'question': 'i am a construction company. Can i apply?', 'response': 'To apply for the tender for the Construction of City Gate Station (CGS), Mother Station, and associated works for the CGD project beside Goa, you must meet the following mandatory requirements:\n\n1. Submit your bid before the closing date (2025-12-19).\n2. Submit the bid in offline mode as specified in the tender.\n3. Provide an Earnest Money Deposit (EMD) of INR 600,000.\n4. Have completed at least one similar project of value ≥ INR 300 million in the last 5 years, or two or more similar projects of value ≥ INR 150 million each in the last 5 years.\n5. Employ a Project Manager with at least 10 years’ experience in similar works, and at least two engineers with 5 years’ experience in CGD/CGS/Mother Station projects.\n6. Provide proof of ownership/lease of major construction equipment required for the project.\n7. Have an average annual turnover of at least INR 200 million in the last 3 financial years, and a positive net worth in the last financial year.\n8. Submit all required forms, declarations, and statutory documents (GST, PAN, ISO 9001, etc.).\n9. Submit a detailed technical proposal and project schedule as per the tender requirements.\n10. Ensure your financial offer is within the budget cap of INR 600 million.\n\nFailure to meet any of these requirements will result in disqualification. If you meet all, you are eligible to apply for this tender beside Goa.', 'created_at': '2025-08-01 14:31:00'}, {'id': '688ccfb3c234cae92002cde1', 'company': 'gRAY mATRIX', 'question': 'WHAT IS THE BIUDGET????', 'response': 'The budget for this tender beside Goa is INR 600,000,000 (Six Hundred Million Indian Rupees).', 'created_at': '2025-08-01 14:31:15'}, {'id': '68904425ec0fb1dab07556d1', 'company': 'XYZ', 'question': 'New Query', 'response': 'No query was provided. Please specify your question related to the tender “CONSTRUCTION OF CITY GATE STATION (CGS) CUM MOTHER STATION & ASSOCIATED WORKS FOR CGD PROJECT BESIDE GOA” for resolution. Out of domain or unrelated questions will not be addressed.', 'created_at': '2025-08-04 05:24:53'}]}}
        This is a mock Bid Evauation Report argument:
        {'name': 'BPCL Bid Evaluation Report', 'context': {'tender': {'id': '688ca34dd73fc89ac2e2c888', 'title': 'CONSTRUCTION OF CITY GATE STATION (CGS) CUM MOTHER STATION & ASSOCIATED WORKS FOR CGD PROJECT AT PERUNDURAI DISTRICT OF ERODE GA IN THE STATE OF TAMILNADU', 'department': 'Construction', 'budget': 600000000, 'emd': 600000, 'opening_date': '2025-06-19', 'closing_date': '2025-12-19', 'status': 'LIVE'}, 'bids': [{'id': '688cb40205940af73b48392a', 'company': 'KSR & SJ INFRASTRUCTURE', 'amount': 400000000000, 'emd_status': 'NULL', 'score': 0, 'pq': False, 'tq': False, 'reasoning': 'Disqualified due to non-compliance with mandatory requirements: EMD not submitted and bid amount vastly exceeds budget cap. Not eligible for further consideration.', 'created_at': '2025-07-31 09:22:29', 'updated_at': '2025-07-31 09:22:29', 'financials': 'See Financial_Document.pdf'}, {'id': '688cb5a6f214e63ccc20cd02', 'company': 'KSR & SJ INFRASTRUCTURE', 'amount': 400000000000, 'emd_status': 'NULL', 'score': 0, 'pq': False, 'tq': False, 'reasoning': 'Disqualified due to non-compliance with mandatory requirements: EMD not submitted and bid amount vastly exceeds budget cap. Not eligible for further consideration.', 'created_at': '2025-07-31 09:22:29', 'updated_at': '2025-07-31 09:22:29', 'financials': 'See Financial_Document.pdf'}, {'id': '688cb842f214e63ccc20cd03', 'company': 'KSR & SJ INFRASTRUCTURE', 'amount': 500000000, 'emd_status': 'NULL', 'score': 0, 'pq': False, 'tq': False, 'reasoning': 'Disqualified due to non-compliance with mandatory requirements: EMD not submitted. Not eligible for further consideration.', 'created_at': '2025-07-31 09:22:29', 'updated_at': '2025-07-31 09:22:29', 'financials': 'See Financial_Document.pdf'}, {'id': '688cb97122e21332c9c58537', 'company': 'KSR & SJ INFRASTRUCTURE', 'amount': 500000000, 'emd_status': 'NULL', 'score': 0, 'pq': False, 'tq': False, 'reasoning': 'Disqualified due to non-compliance with mandatory requirements: EMD not submitted. Not eligible for further consideration.', 'created_at': '2025-07-31 09:22:29', 'updated_at': '2025-07-31 09:22:29', 'financials': 'See Financial_Document.pdf'}, {'id': '688cba247149ee52708b40e5', 'company': 'KSR & SJ INFRASTRUCTURE', 'amount': 500000000, 'emd_status': 'NULL', 'score': 0, 'pq': False, 'tq': False, 'reasoning': 'Disqualified due to non-compliance with mandatory requirements: EMD not submitted. Not eligible for further consideration.', 'created_at': '2025-07-31 09:22:29', 'updated_at': '2025-07-31 09:22:29', 'financials': 'See Financial_Document.pdf'}, {'id': '688cbdf2e6d64c6f05874084', 'company': 'KSR & SJ INFRASTRUCTURE', 'amount': 500000000, 'emd_status': 'PAID', 'score': 82, 'pq': True, 'tq': True, 'reasoning': 'Compliant with most requirements. Strong technical and operational proposal. Average turnover slightly below threshold and ISO/QA plan not explicit, but otherwise eligible and scored 82/100.', 'created_at': '2025-07-31 09:22:29', 'updated_at': '2025-07-31 09:22:29', 'financials': 'See Financial_Document.pdf'}]}}

    Returns:
        str: The S3 URL of the uploaded PDF file.

    Raises:
        ValueError: If name is empty or context is not a valid dictionary.
        RuntimeError: If template fetching, rendering, PDF generation, or S3 upload fails.
    """

    if not name or not context:
        raise ValueError("name and context must be provided")
    if name not in ["Query Document", "Tender Document", "Bid Evaluation Report"]:
        raise ValueError("Invalid template name")

    template = await DocumentTemplate.find_one(DocumentTemplate.name == name)
    if not template:
        raise ValueError("Template not found")

    template_content = template.template

    # Create Jinja2 environment with custom filters
    env = Environment()
    env.filters["nl2br"] = nl2br
    env.filters["format_currency"] = format_currency
    env.filters["format_date"] = format_date

    jinja_template = env.from_string(template_content)
    rendered = jinja_template.render(**context)

    path_to_wkhtmltopdf = SETTINGS.WKHTML_PATH
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
    options = {
        "page-size": "A4",
        "margin-top": "1in",
        "margin-right": "1in",
        "margin-bottom": "1in",
        "margin-left": "1in",
        "encoding": "UTF-8",
        "quiet": "",
    }
    pdf_bytes = pdfkit.from_string(
        rendered, False, options=options, configuration=config
    )

    filename = f"{uuid.uuid4()}.pdf"

    s3_url = upload_to_s3(
        file_bytes=pdf_bytes, filename=filename, content_type="application/pdf"
    )
    return s3_url

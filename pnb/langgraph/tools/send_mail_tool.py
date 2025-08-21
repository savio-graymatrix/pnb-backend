import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import os
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from pnb import SETTINGS, LOGGER
from pnb.db.data_models.generic.DocumentTemplate import DocumentTemplate
from jinja2 import Template, Environment
from .template_to_pdf import nl2br, format_currency, format_date
from datetime import datetime


async def send_mail(
    subject: str,
    body: str,
    is_html: bool = False,
    sender_email: str = SETTINGS.EMAIL_HOST_USER,
    recipient_email: str = SETTINGS.RECIPIENT_EMAIL,
) -> Dict[str, Any]:
    """
    Send an email using SendinBlue's SMTP relay.

    Args:
        subject (str): Email subject line.
        body (str): Email body content (plain text or HTML).
        is_html (bool, optional): Whether the body is HTML. Defaults to False (plain text).
        sender_email (str, optional): Sender's email address.
        recipient_email (str, optional): Recipient's email address.

    Returns:
        Dict[str, Any]: Result with success status and data or error message.
    """
    smtp_config = {
        "host": SETTINGS.EMAIL_HOST,
        "port": SETTINGS.EMAIL_PORT,
        "secure": False,
        "auth": {
            "user": SETTINGS.EMAIL_HOST_USER,
            "pass": SETTINGS.EMAIL_HOST_PASSWORD,
        },
        "tls": {"rejectUnauthorized": False},
    }

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject.strip()

    # Attach body (plain text or HTML)
    if is_html:
        template = await DocumentTemplate.find_one(
            DocumentTemplate.name == "PNB Email Template"
        )
        if not template:
            raise ValueError("Template not found")

        template_content = template.template

        # Create Jinja2 environment with custom filters
        env = Environment()
        env.filters["nl2br"] = nl2br
        env.filters["format_currency"] = format_currency
        env.filters["format_date"] = format_date
        context = {
            "subject": subject,
            "body": body,
            "current_date": datetime.now(),
            "company_name": "Punjab National Bank",
            "cta_url": "https://en.wikipedia.org/wiki/Punjab_National_Bank",
        }
        jinja_template = env.from_string(template_content)
        rendered = jinja_template.render(**context)
        msg.attach(MIMEText(rendered.strip(), "html"))
    else:
        msg.attach(MIMEText(body.strip(), "plain"))

    try:
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            server.starttls()
            server.login(smtp_config["auth"]["user"], smtp_config["auth"]["pass"])
            server.send_message(msg)
        return {"success": True, "message": f"Email Sent to {recipient_email}"}
    except smtplib.SMTPException as e:
        return {"success": False, "error": f"Failed to send email: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}"}


@tool
async def handle_email(
    subject: str,
    body: str,
    is_html: bool = False,
    recipient_email: str = SETTINGS.RECIPIENT_EMAIL,
    sender_email: str = SETTINGS.EMAIL_HOST_USER,
) -> Dict[str, Any]:
    """
    Tool to handle sending an email

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
        is_html (bool, optional): Whether the body is HTML. Defaults to False.
        recipient_email (str, optional): Recipient's email address.
        sender_email (str, optional): Sender's email address.
    Returns:
        Dict[str, Any]: Result with success status and message.
    """
    try:
        result = await send_mail(
            subject=subject,
            body=body,
            is_html=is_html,
            sender_email=SETTINGS.EMAIL_HOST_USER,
            recipient_email=SETTINGS.RECIPIENT_EMAIL,
        )
        if result["success"]:
            return {"status": "success", "message": result["message"]}
        else:
            LOGGER.error(result["error"])
            return {"status": "error", "message": result["error"]}

    except Exception as e:
        LOGGER.error(str(e))
        return {"status": "error", "message": f"Error: {str(e)}"}

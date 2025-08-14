import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import os
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from pnb import SETTINGS, LOGGER


async def send_mail(
    subject: str,
    body: str,
    is_html: bool = False,
    sender_email: str = SETTINGS.EMAIL_HOST_USER,
) -> Dict[str, Any]:
    """
    Send an email using SendinBlue's SMTP relay.

    Args:
        subject (str): Email subject line.
        body (str): Email body content (plain text or HTML).
        is_html (bool, optional): Whether the body is HTML. Defaults to False (plain text).
        sender_email (str, optional): Sender's email address. Defaults to 'itsupport@graymatrix.com'.

    Returns:
        Dict[str, Any]: Result with success status and data or error message.
    """
    recipient_email = SETTINGS.RECIPIENT_EMAIL
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
        msg.attach(MIMEText(body.strip(), "html"))
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
    subject: str, body: str, is_html: bool = False
) -> Dict[str, Any]:
    """
    Tool to handle sending an email

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
        is_html (bool, optional): Whether the body is HTML. Defaults to False.

    Returns:
        Dict[str, Any]: Result with success status and message.
    """
    try:
        result = await send_mail(subject, body, is_html)
        if result["success"]:
            return {"status": "success", "message": result["message"]}
        else:
            LOGGER.error(result["error"])
            return {"status": "error", "message": result["error"]}

    except Exception as e:
        LOGGER.error(str(e))
        return {"status": "error", "message": f"Error: {str(e)}"}

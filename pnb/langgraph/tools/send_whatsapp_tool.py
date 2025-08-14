import requests
from typing import Dict, Any
from pnb import SETTINGS, LOGGER
from langchain_core.tools import tool
import asyncio
import json


async def send_whatsapp_message(message_text: str, phone_number: str) -> Dict[str, Any]:
    """
    Send a text message via the WhatsApp Business API.

    Args:
        message_text (str): The text content of the message.
        phone_number (str): The phone number to send the message to.

    Returns:
        Dict[str, Any]: Result with success status and data or error message.
    """
    print(SETTINGS.WHATSAPP_GM)
    print(type(SETTINGS.WHATSAPP_GM))
    # payload = {
    #     "messaging_product": "whatsapp",
    #     "recipient_type": "individual",
    #     "to": SETTINGS.WHATSAPP_GM,
    #     "type": "text",
    #     "text": {"preview_url": False, "body": message_text.strip()},
    # }
    payload = {
        "access_token": "OfRqofjLdVUUikdj",
        "session": SETTINGS.WHATSAPP_GM,
        "message": [
            {
                "message": {
                    "template": {
                        "elements": {"title": message_text.strip()},
                        "type": "Card",
                    }
                }
            }
        ],
        "platform": "WhatsApp",
    }
    try:
        response = requests.post(
            f"{SETTINGS.WHATSAPP_API}",
            data=json.dumps(payload),
            headers={
                "Authorization": f"Bearer {SETTINGS.WHATSAPP_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
        )
        LOGGER.debug(response.content)
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.RequestException as e:
        LOGGER.error(str(e))
        return {"success": False, "error": f"Failed to send message: {str(e)}"}


@tool
async def handle_text_message(message_text: str, phone_number: str) -> Dict[str, Any]:
    """
    Handle a WhatsApp text message request for an agent.

    Args:
        message_text (str): The text content to send.
        phone_number (str): The phone number to send the message to.

    Returns:
        Dict[str, Any]: Result with success status and message.
    """

    try:
        result = await send_whatsapp_message(
            message_text=message_text, phone_number=phone_number
        )
        if result["success"]:
            return {"status": "success", "message": "Message sent successfully"}
    except Exception as e:
        LOGGER.error(str(e))
        return {"status": "error", "message": str(e)}


# res = asyncio.run(handle_text_message.ainvoke("Hello"))
# print(res)

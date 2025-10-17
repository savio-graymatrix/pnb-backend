import requests
from typing import Dict, Any
from pnb import SETTINGS, LOGGER
from langchain_core.tools import tool
from pnb.db.data_models.sales.Customer import Customer
from pnb.db.data_models.sales.Lead import Lead
from beanie import PydanticObjectId
import asyncio
import json


async def _resolve_customer(identifier: str) -> Customer | None:
    if not identifier:
        return None

    # Try MongoDB ObjectId first
    try:
        customer = await Customer.get(PydanticObjectId(identifier))
        if customer:
            return customer
    except Exception:
        pass

    # Fall back to business-facing identifiers
    customer = await Customer.find_one({"customer_id": identifier})
    if customer:
        return customer

    return await Customer.find_one(
        {"name": {"$regex": f"^{identifier}$", "$options": "i"}}
    )


async def _resolve_lead(identifier: str) -> Lead | None:
    if not identifier:
        return None

    try:
        lead = await Lead.get(PydanticObjectId(identifier))
        if lead:
            return lead
    except Exception:
        pass

    lead = await Lead.find_one({"name": {"$regex": f"^{identifier}$", "$options": "i"}})
    if lead:
        return lead

    return await Lead.find_one({"contact.phone": identifier})


async def send_whatsapp_message(
    message_text: str, phone_number: str, image_url: str = None
) -> Dict[str, Any]:
    """
    Send a text message via the WhatsApp Business API.

    Args:
        message_text (str): The text content of the message.
        phone_number (str): The phone number to send the message to.
        image_url (str, optional): The URL of the image to attach to the message.

    Returns:
        Dict[str, Any]: Result with success status and data or error message.
    """
    # print(SETTINGS.WHATSAPP_GM)
    # print(type(SETTINGS.WHATSAPP_GM))
    # payload = {
    #     "messaging_product": "whatsapp",
    #     "recipient_type": "individual",
    #     "to": SETTINGS.WHATSAPP_GM,
    #     "type": "text",
    #     "text": {"preview_url": False, "body": message_text.strip()},
    # }
    payload = {
        "access_token": "OfRqofjLdVUUikdj",
        "session": phone_number,
        "message": [
            {
                "message": {
                    "template": {
                        "elements": {
                            "title": message_text.strip(),
                            "buttons": [
                                {
                                    "title": "Buy Now",
                                    "payload": "/buy_now_car_insurance",
                                    "type": "postback",
                                    "mode": "disable_text_box",
                                },
                                {
                                    "title": "I have question",
                                    "payload": "I have question regarding how to buy gold",
                                    "type": "close_chat",
                                    "mode": "disable_text_box",
                                },
                            ],
                        },
                        "type": "Card",
                    }
                }
            }
        ],
        "platform": "WhatsApp",
    }

    # Add attachment if image_url is provided
    if image_url:
        payload["message"][0]["message"]["template"]["elements"]["attachment"] = {
            "is_download": False,
            "url": image_url,
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
async def handle_text_message(
    message_text: str, id: str, db: str, image_url: str = None
):
    """
    Tool to send whatsapp message after retrieving contact details from the db

    Args:
        message_text: str
        Markdown standards for the whatsapp text to send:
        - Use * for bold text
        - Use _ for italic text

        (Eg: *Hi Mamta!* 👋

Thank you for your interest in *T Bank's Premium Home Loan* -- where your dream home becomes a reality with *exclusive low rates*, *flexible repayment options*, and *dedicated expert support* every step of the way.

✨ With our Home Loan, you can:\
✅ Secure your dream home easily\
✅ Enjoy attractive interest rates\
✅ Customize your repayment plan as per your convenience

📞 Would you like to *know more* or *schedule a free call* 📲 with our Home Loan Specialist?

Just reply to this message, and we'll take care of the rest! 😊

*Best regards,*\
*T Solutions*)
        id: str (The _id of the Lead or Customer document)
        db: str (Lead or Customer)
        image_url: str (optional)

    """
    if db == "Lead":
        lead = await _resolve_lead(id)
        # print("lead details: ", lead)
        if not lead or not lead.contact or not lead.contact.phone:
            return {"status": "error", "message": "Lead contact details unavailable"}

        phone_number = lead.contact.phone
        try:
            result = await send_whatsapp_message(message_text, phone_number, image_url)
            if result["success"]:
                return {"status": "success", "message": "Message sent successfully"}
        except Exception as e:
            LOGGER.error(str(e))
            return {"status": "error", "message": str(e)}
    elif db == "Customer":
        customer = await _resolve_customer(id)
        # print("customer details: ", customer)
        if not customer or not customer.contact:
            return {
                "status": "error",
                "message": "Customer contact details unavailable",
            }

        phone_number = customer.contact
        try:
            result = await send_whatsapp_message(message_text, phone_number, image_url)
            if result["success"]:
                return {"status": "success", "message": "Message sent successfully"}
        except Exception as e:
            LOGGER.error(str(e))
            return {"status": "error", "message": str(e)}

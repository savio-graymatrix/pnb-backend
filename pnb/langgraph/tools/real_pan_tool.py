from langchain_core.tools import tool
from pnb.core.settings import SETTINGS
from pnb import LOGGER
import requests
import json
import re
import asyncio
import hashlib
import base64

# Configuration (add to your SETTINGS object)
DEV_SANDBOX_API_KEY = SETTINGS.DEV_SANDBOX_API_KEY
DEV_SANDBOX_API_SECRET = SETTINGS.DEV_SANDBOX_API_SECRET
SANDBOX_BASE_URL = SETTINGS.SANDBOX_BASE_URL


async def get_jwt_token() -> str:
    """
    Authenticate with Sandbox API to obtain a JWT token using SHA-256 hashed credentials.

    Returns:
        str: JWT token.

    Raises:
        Exception: If authentication fails.
    """
    auth_url = f"{SANDBOX_BASE_URL}/authenticate"
    # Ensure credentials are encoded as UTF-8 with no extra whitespace
    credentials = f"{DEV_SANDBOX_API_KEY}:{DEV_SANDBOX_API_SECRET}".encode(
        "utf-8"
    ).strip()
    hashed_credentials = hashlib.sha256(credentials).digest()
    encoded_credentials = base64.b64encode(hashed_credentials).decode("utf-8").strip()
    payload = {}

    headers = {
        "x-api-key": "key_test_c9ee0299cebb4f9683bcac15ab9aea29",
        "Authorization": f"Token={encoded_credentials}",
        "x-api-secret": "secret_test_0bf58d996a434ad6b9f538f1d1ddc9fa",
    }
    try:
        response = requests.request("POST", auth_url, headers=headers, data=payload)

        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            raise Exception(
                f"Authentication failed: {response.status_code} - {response.text}"
            )
    except Exception as e:
        raise Exception(f"Authentication error: {str(e)}")


async def verify_pan(pan: str, name: str, dob: str):
    """
    Verify PAN details using Sandbox API.

    Args:
        pan (str): PAN number (e.g., ABCPV1234D).
        name (str): Name on PAN card (e.g., John Doe).
        dob (str): Date of birth in DD/MM/YYYY format (e.g., 01/01/2000).

    Returns:
        Dict[str, Any]: PAN verification details or error message.
    """
    pan_url = SETTINGS.SANDBOX_PAN_URL
    jwt_token = await get_jwt_token()
    headers = {
        "Authorization": f"{jwt_token}",
        "x-api-key": f"{DEV_SANDBOX_API_KEY}",
        "accept": "application/json",
        "content-type": "application/json",
    }
    payload = {
        "@entity": "in.co.sandbox.kyc.pan_verification.request",
        "pan": f"{pan}",
        "name_as_per_pan": f"{name}",
        "date_of_birth": f"{dob}",
        "consent": "Y",
        "reason": "KYC verification",
    }
    try:
        response = requests.post(pan_url, headers=headers, json=payload)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 422:
            return {"success": False, "error": "Invalid PAN format or missing consent"}
        elif response.status_code == 401:
            return {
                "success": False,
                "error": "Authentication failed (token may be expired)",
            }
        else:
            return {
                "success": False,
                "error": f"Error: {response.status_code} - {response.text}",
            }
    except Exception as e:
        LOGGER.error(f"PAN verification error: {str(e)}")
        return {"success": False, "error": f"Error: {str(e)}"}


@tool
async def handle_pan_verify(pan: str, name: str, dob: str):
    """
    Tool to verify PAN details using Sandbox API.

    Args:
        pan (str): PAN number (e.g., ABCPV1234D).
        name (str): Name as per PAN card.
        dob (str): Date of birth in DD/MM/YYYY format.

    Returns:
        Dict[str, Any]: Result with success status and PAN details or error message.
    """

    try:
        # Verify PAN
        result = await verify_pan(pan, name, dob)
        if not result["success"]:
            LOGGER.error(result["error"])
            return {"status": "error", "message": result["error"]}

        return {
            "status": "success",
            "message": "PAN verified successfully",
            "data": result,
        }

    except Exception as e:
        LOGGER.error(str(e))
        return {"status": "error", "message": f"Error: {str(e)}"}

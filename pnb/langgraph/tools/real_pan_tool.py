import requests
import json
from langchain_core.tools import tool
from pnb import SETTINGS, LOGGER

# Configuration (add to your SETTINGS object)
DEV_SANDBOX_API_KEY = SETTINGS.DEV_SANDBOX_API_KEY
DEV_SANDBOX_API_SECRET = SETTINGS.DEV_SANDBOX_API_SECRET
SANDBOX_BASE_URL = SETTINGS.SANDBOX_BASE_URL


async def get_jwt_token():
    """
    Authenticate with Sandbox API to obtain a JWT token.

    Returns:
        str: JWT token.

    Raises:
        Exception: If authentication fails.
    """
    auth_url = f"{SANDBOX_BASE_URL}/authenticate"
    headers = {"Content-Type": "application/json", "x-api-key": DEV_SANDBOX_API_KEY}
    payload = {"api_key": DEV_SANDBOX_API_KEY, "api_secret": DEV_SANDBOX_API_SECRET}
    try:
        response = requests.post(auth_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            raise Exception(
                f"Authentication failed: {response.status_code} - {response.text}"
            )
    except Exception as e:
        LOGGER.error(f"Authentication error: {str(e)}")
        raise


async def verify_pan(pan: str, name: str, dob: str):
    """
    Verify PAN details using Sandbox API.

    Args:
        pan (str): PAN number (e.g., ABCPV1234D).
        name (str): Name as per PAN card.
        dob (str): Date of birth in DD/MM/YYYY format.

    Returns:
        Dict[str, Any]: PAN verification details or error message.
    """
    verify_url = f"{SANDBOX_BASE_URL}/kyc/pan/verify"
    jwt_token = await get_jwt_token()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "x-api-key": DEV_SANDBOX_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "@entity": "in.co.sandbox.kyc.pan_verification.request",
        "pan": pan,
        "name_as_per_pan": name,
        "date_of_birth": dob,
        "consent": "Y",
        "reason": "KYC verification",
    }
    try:
        response = requests.post(verify_url, headers=headers, data=json.dumps(payload))
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

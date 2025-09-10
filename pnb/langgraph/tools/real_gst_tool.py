from langchain_core.tools import tool
from pnb.core.settings import SETTINGS
import requests
import json
import re
import asyncio
import hashlib
import base64

# Configuration from SETTINGS
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


async def search_gstin(gstin: str, jwt_token: str) -> dict:
    """
    Search GSTIN details using Sandbox API.

    Args:
        gstin (str): The GSTIN number to search (e.g., 29HJKPS9689A8Z5).
        jwt_token (str): The JWT token for authentication.

    Returns:
        dict: The GSTIN details or error information.
    """
    gst_url = SETTINGS.SANDBOX_GST_URL
    headers = {
        "Authorization": f"{jwt_token}",
        "x-api-key": f"{DEV_SANDBOX_API_KEY}",
        "accept": "application/json",
        "content-type": "application/json",
    }
    try:
        response = requests.post(gst_url, headers=headers, json={"gstin": gstin})
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 422:
            return {"success": False, "error": "Invalid GSTIN format"}
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
        return {"success": False, "error": f"Error: {str(e)}"}


@tool
async def handle_gstin_search(gstin: str):
    """
    Tool to verify GSTIN details using Sandbox API.

    Args:
        gstin (str): GSTIN to verify (e.g., 29HJKPS9689A8Z5).

    Returns:
        dict: Result with success status and GSTIN details or error message.
    """

    try:
        # Get JWT token
        jwt_token = await get_jwt_token()

        # Search GSTIN
        result = await search_gstin(gstin, jwt_token)
        if not result["success"]:
            return {"status": "error", "message": result["error"]}

        # Format response
        gst_data = result["data"]
        return gst_data
    except Exception as e:
        # Uncomment if LOGGER is defined in pnb
        # from pnb import LOGGER
        # LOGGER.error(str(e))
        return {"status": "error", "message": str(e)}


# Example test code
# async def test():
#     result = await handle_gstin_search("29HJKPS9689A8Z5")
#     print(json.dumps(result, indent=2))
#
# if __name__ == "__main__":
#     asyncio.run(test())

# Example test code
# async def test():
#     result = await handle_gstin_search("29HJKPS9689A8Z5")
#     print(json.dumps(result, indent=2))
#
# if __name__ == "__main__":
#     asyncio.run(test())

from langchain_core.tools import tool

# from pnb.core.settings import SETTINGS
import requests
import json
import asyncio

# DEV_SANDBOX_API_KEY = SETTINGS.DEV_SANDBOX_API_KEY
# DEV_SANDBOX_API_SECRET = SETTINGS.DEV_SANDBOX_API_SECRET
# SANDBOX_BASE_URL = SETTINGS.SANDBOX_BASE_URL

DEV_SANDBOX_API_KEY = "key_test_c9ee0299cebb4f9683bcac15ab9aea29"
DEV_SANDBOX_API_SECRET = "secret_test_0bf58d996a434ad6b9f538f1d1ddc9fa"
SANDBOX_BASE_URL = "https://api.sandbox.co.in"


async def get_jwt_token():
    """
    Authenticate with Sandbox API to obtain a JWT token.

    Returns:
        str: JWT token.

    Raises:
        Exception: If authentication fails.
    """
    auth_url = f"{SANDBOX_BASE_URL}/auth"
    headers = {
        "Content-Type": "applicaiton/json",
        "x-api-key": DEV_SANDBOX_API_KEY,
    }
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


async def search_gstin(gstin: str, jwt_token: str):
    """
    Search GSTIN details using Sandbox API

    Args:
        gstin (str): The gstin number to search
        jwt_token (str): The JWT token for authentication

    Returns:
        dict: The GSTIN details
    """

    gst_url = f"{SETTINGS.SANDBOX_BASE_URL}/gsp/public/gstin/{gstin}"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "x-api-key": SETTINGS.DEV_SANDBOX_API_KEY,
        "Accept": "application/json",
    }
    try:
        response = requests.get(gst_url, headers=headers)
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
        LOGGER.error(f"GSTIN search error: {str(e)}")
        return {"success": False, "error": f"Error: {str(e)}"}


@tool
async def handle_gstin_search(gstin: str):
    """
    Tool to verify GSTIN details using Sandbox API.

    Args:
        gstin (str): GSTIN to verify (e.g., 29HJKPS9689A8Z5).

    """

    try:
        # Get JWT token
        jwt_token = await get_jwt_token()

        # Search GSTIN
        result = await search_gstin(gstin, jwt_token)
        if not result["success"]:
            LOGGER.error(result["error"])
            return {"status": "error", "message": result["error"]}

        return result

    except Exception as e:
        LOGGER.error(str(e))
        return {"status": "error", "message": str(e)}


# result = asyncio.run(handle_gstin_search("29HJKPS9689A8Z5"))
async def test():
    result = await handle_gstin_search("29HJKPS9689A8Z5")
    print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test())

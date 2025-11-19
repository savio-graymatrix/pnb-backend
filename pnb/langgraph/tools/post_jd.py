from langchain.tools import tool
from enum import Enum
import requests
from pnb import LOGGER
import traceback


class Platform(Enum):
    LINKEDIN = "linkedin"


class PostVisibility(Enum):
    PUBLIC = "PUBLIC"
    CONNECTIONS = "CONNECTIONS"


CAREERS_LINKEDIN_API = (
    "https://f570xwfso8.execute-api.ap-south-1.amazonaws.com/dev/api/linkedin/post"
)


@tool
def post_jd(jd_text: str, platform: Platform = Platform.LINKEDIN):
    """Create a Post from JD Text based on the platform provided

    :params:
    jd_text (str): JD Text in Unicode
    platform (Platform): Platform to post on

    """
    try:
        match (platform):
            case Platform.LINKEDIN:
                response = requests.post(
                    CAREERS_LINKEDIN_API,
                    json={"text": jd_text, "visibility": PostVisibility.PUBLIC.value},
                )
                response.raise_for_status()
                data = response.json()
                if "postUrl" in data.keys():
                    return f"Post is sent to LinkedIn : {data['postUrl']}"
                else:
                    return "Post is sent to LinkedIn : URL not provided"
            case _:
                raise ValueError(f"Unsupported platform: {platform}")
    except Exception as e:
        LOGGER.error(traceback.format_exc())
        return "Post is not sent to Platform"

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
    """ """
    try:
        match (platform):
            case Platform.LINKEDIN:
                response = requests.post(
                    CAREERS_LINKEDIN_API,
                    json={"text": jd_text, "visibility": PostVisibility.PUBLIC.value},
                )
                response.raise_for_status()
                return "Post is sent to LinkedIn"
            case _:
                raise ValueError(f"Unsupported platform: {platform}")
    except Exception as e:
        LOGGER.error(traceback.format_exc())
        return "Post is not sent to Platform"

from langchain_core.tools import tool
import os
from dotenv import load_dotenv

load_dotenv()

# API_URL= os.getenv("API_URL")
API_URL = "https://dummy_api.com"


@tool
async def job_post_to_linkedin(job_id: str, job_title: str, job_description: str):
    """
    Tool to post a job to Linkedin

    Args:
        job_id: The job id
        job_title: The job title
        job_description: The job description

    Returns:
        True if the job was posted to Linkedin else False

    Raises:
        Exception if the job was not posted to Linkedin
    """
    try:
        result = await post_job(job_id, job_title, job_description)
        return result
    except Exception as e:
        return f"Failed to post job to linkedin {e}"


async def post_job(job_id: str, job_title: str, job_description: str):
    try:
        result = await API_URL.post(job_id, job_title, job_description)
        # return result
        return True
    except Exception as e:
        return f"Failed to post job to linkedin {e}"

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import List
import aiohttp


class SaveJDInput(BaseModel):
    role: str = Field(..., description="The job role (e.g., Software Engineer)")
    experience: float = Field(..., description="Experience required in years (e.g., 2.0, 5.5)")
    skills: List[str] = Field(..., description="List of skills required (e.g., ['Python', 'SQL', 'AWS'])")
    location: List[str] = Field(..., description="List of job locations (e.g., ['Mumbai', 'Remote'])")
    jd_text: str = Field(..., description="The complete Job Description text")


API_URL = "https://qxv1b5zbuh.execute-api.us-east-1.amazonaws.com/dev/api/jobs/create-job-description"


async def _save_jd_tool(role: str, experience: float, skills: List[str], location: List[str], jd_text: str) -> str:
    """Async wrapper for saving JD into the external API instead of MySQL."""
    payload = {
        "role": role,
        "experience": experience,
        "skills": skills,
        "location": location,
        "jd_text": jd_text,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success") == 1:
                    return f"✅ Job description saved successfully! ID: {data['data']['id']}"
                else:
                    return f"❌ Failed to save JD: {data.get('message', 'Unknown error')}"
            else:
                return f"❌ API request failed with status {response.status}"


save_jd_tool = StructuredTool.from_function(
    func=_save_jd_tool,
    name="save_jd",
    description="Save the generated Job Description using the external API",
    args_schema=SaveJDInput,
    coroutine=_save_jd_tool,  # ensures async execution
)

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from pnb.db.stores.jd_stores.database.jd_repository import save_jd
from typing import List


class SaveJDInput(BaseModel):
    role: str = Field(..., description="The job role (e.g., Software Engineer)")
    experience: float = Field(..., description="Experience required in years (e.g., 2.0, 5.5)")
    skills: List[str] = Field(..., description="List of skills required (e.g., ['Python', 'SQL', 'AWS'])")
    location: List[str] = Field(..., description="List of job locations (e.g., ['Mumbai', 'Remote'])")
    jd_text: str = Field(..., description="The complete Job Description text")


async def _save_jd_tool(role: str, experience: float, skills: List[str], location: List[str], jd_text: str) -> str:
    """Async wrapper for saving JD into the database."""
    return await save_jd(role, experience, skills, location, jd_text)


save_jd_tool = StructuredTool.from_function(
    func=_save_jd_tool,
    name="save_jd",
    description="Save the generated Job Description into MySQL database",
    args_schema=SaveJDInput,
    coroutine=_save_jd_tool,  # ensures async execution
)

from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import List
import json


class Button(BaseModel):
    title: str = Field(description="The short title of the prompt")
    prompt: str = Field(description="The prompt for the guidance to the user")


@tool
async def button_tool(buttons: List[Button]):
    """
    Tool to display buttons with their titles and prompts for frontend user guidance of the next steps

    Args:
        buttons (List[Button]): List of buttons to display
    """
    buttons_dict = [button.model_dump() for button in buttons]
    return json.dumps(buttons_dict)

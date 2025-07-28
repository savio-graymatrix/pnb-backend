from beanie import Document, PydanticObjectId
from typing import Optional, List
from pydantic import BaseModel

class Instruction(Document):
    content: str
    class Settings:
        name = "instruction"

class UpdateInstruction(Instruction):
    content: Optional[str]

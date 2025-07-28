from beanie import Document, PydanticObjectId
from typing import Optional, List
from pydantic import BaseModel, Field

class Instruction(Document):
    content: str
    class Settings:
        name = "instruction"

class UpdateInstruction(Instruction):
    content: Optional[str]

class InstructionSet(BaseModel):
    instruction_set: List[str] = Field(description="The list of the instructions")
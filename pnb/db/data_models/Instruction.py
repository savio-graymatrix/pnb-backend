from beanie import Document, PydanticObjectId
from typing import Optional, List
from pydantic import BaseModel

class Instruction(Document):
    content: str
    # instruction_set_id: PydanticObjectId
    class Settings():
        name = "instruction"

class UpdateInstruction(Instruction):
    content: Optional[str]

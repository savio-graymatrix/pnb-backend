from beanie import Document, PydanticObjectId
from typing import Optional

class Instruction(Document):
    content: str
    instruction_set_id: PydanticObjectId
    class Settings():
        name = "instruction"

class UpdateInstruction(Instruction):
    content: Optional[str]
    instruction_set_id: Optional[PydanticObjectId]

class CreateInstruction(Instruction):
    pass
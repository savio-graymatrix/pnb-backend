from beanie import Document, PydanticObjectId
from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime, timezone
from typing import Optional, List, Literal

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
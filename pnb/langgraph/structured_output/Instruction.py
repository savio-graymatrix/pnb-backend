from pydantic import BaseModel, Field   
from typing import List


class Instruction(BaseModel):
    instruction: str = Field(description="The instruction set in  as in the response by the 'instruction_agent'")

class InstructionSet(BaseModel):
    instruction_set: List[Instruction] = Field(description="The list of the instructions")
 
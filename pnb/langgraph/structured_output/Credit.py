from turtle import title
from pydantic import BaseModel, Field   
from typing import List


# class Credit(BaseModel):
#     instruction: s

class Financial(BaseModel):
    title: str = Field(description="The title of the financial")
    description: str = Field(description="The description of the financial")


class Credit(BaseModel):
    pan_verification: str = Field(description="The pan verification in  as in the response by the 'pan_agent'")
    aadhar_verification: str = Field(description="The aadhar verification in  as in the response by the 'aadhar_agent'")
    loan_type: str = Field(description="The loan type in  as in the response by the 'credit_assist_agent'")
    financials: List[Financial] = Field(description="The financials in  as in the response by the 'credit_assist_agent'")
    risk_grade: str = Field(description="The risk grade in  as in the response by the 'credit_assist_agent'")
    recommendation: str = Field(description="The recommendation in  as in the response by the 'credit_assist_agent'")
 
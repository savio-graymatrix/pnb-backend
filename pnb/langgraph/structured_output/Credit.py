#from turtle import title
from pydantic import BaseModel, Field   
from typing import List, Literal


# class Credit(BaseModel):
#     instruction: s

class Review(BaseModel):
    alert: Literal["low_risk", "medium_risk", "high_risk"] = Field(description="The alert as per the 'supervisor'")
    title: str = Field(description="The title of the review as in the response by the 'supervisor'")
    message: str = Field(description="The reason of the alert by the 'supervisor'")

class ReviewSet(BaseModel):
    reviewSets: List[Review] = Field(description="An array of reviews, each containing an alert, title and a message")

class Financial(BaseModel):
    title: str = Field(description="The title of the financial as in the response by the 'supervisor'")
    description: str = Field(description="The description of the financial as in the response by the 'supervisor'")

class aadhar(BaseModel):
    kyc_status: str = Field(description="The kyc status in  as in the response by the 'supervisor'")
    details: str = Field(description="The details in  as in the response by the 'supervisor'")

class pan(BaseModel):
    kyc_status: str = Field(description="The pan verification in  as in the response by the 'supervisor'")
    details: str = Field(description="The details in  as in the response by the 'supervisor'")


class Credit(BaseModel):
    review_set: ReviewSet = Field(description="The review set in  as in the response by the 'supervisor'")
    pan_verification: pan = Field(description="The pan verification in  as in the response by the 'supervisor'")
    aadhar_verification: aadhar = Field(description="The aadhar verification in  as in the response by the 'supervisor'")
    loan_type: str = Field(description="The loan type in  as in the response by the 'supervisor'")
    financials: List[Financial] = Field(description="The financials in  as in the response by the 'supervisor'")
    risk_grade: str = Field(description="The risk grade in  as in the response by the 'supervisor'")
    recommendation: str = Field(description="The recommendation in  as in the response by the 'supervisor'")
 
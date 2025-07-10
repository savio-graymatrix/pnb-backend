#from turtle import title
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Literal


class Review(BaseModel):
    alert: Literal["no_risk", "medium_risk", "high_risk", "low_risk"] = Field(description="The alert as per the 'credit_assist_agent'")
    title: str = Field(description="The title of the review as in the response by the 'credit_assist_agent'")
    message: str = Field(description="The reason of the alert by the 'credit_assist_agent'. Make sure it is an issue or a discrepancy explicitly.")

class AgentLifeCycle(BaseModel):
    agent_name: str = Field(description="The name of the agent. Please append 'agent' tag to the names and humanise it. You should use the tool names as agents and remove the word 'tool'.")
    reasoning: str = Field(description="The action performed by the agent for their tasks")

class DocumentChecklist(BaseModel):
    document_name: str
    file_url : str
    isVerified : bool

class Credit(BaseModel):
    review_set: List[Review] = Field(description="The review set in as in the response by the 'credit_assist_agent'")
    agent_lifecycle: List[AgentLifeCycle] = Field(description="")
    documents_checklist: List[DocumentChecklist] = Field(description="")

 
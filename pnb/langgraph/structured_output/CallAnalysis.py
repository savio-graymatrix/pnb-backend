from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class CallStatus(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class KeyTitle(BaseModel):
    name: str = Field(description="Title of the quality control criteria")
    list_of_keys: List[str] = Field(
        default_factory=list,
        description="The list of quality control keys",
    )

class KeyTitleWithScore(KeyTitle):
    score: int = Field(description="Quality control score on the basis of the keys and the assessment out of 10")


class ComplianceReport(BaseModel):
    customer_concern: str = Field(description="Customer concern in one line", title="Customer Concern")
    issue_identified: KeyTitle
    resolution: KeyTitle
    upsell_opportunity: KeyTitle
    ai_agent_contribution: KeyTitle
    outcome: KeyTitle


class Scorecard(BaseModel):
    quality_control: KeyTitleWithScore
    ticket_updates: KeyTitleWithScore
    solution_cause: KeyTitleWithScore


class CallAnalysisResult(BaseModel):
    """Structured output for call analysis results"""
    summary: str = Field(description="Comprehensive paragraph summary as proper markdown format")
    compliance_report: ComplianceReport = Field(description="Structured compliance report as proper markdown format")
    scorecard: Scorecard = Field(description="Quality scorecard with scores as proper markdown format")
    overall_score: int = Field(ge=1, le=100, description="Overall score 1-100")
    call_status: CallStatus = Field(description="Overall sentiment of the call")
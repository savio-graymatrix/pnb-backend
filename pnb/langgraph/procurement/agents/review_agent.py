from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from pnb.langgraph.utils import OPENAI_LLM
# from bpcl.agentic.structured_outputs import Review, ReviewSet
# from bpcl.agentic.tools.parser import extract_from_pdf
# from bpcl.db.data_models import InstructionSet, Instruction
# from bpcl.db.data_models import Bid
from bson import ObjectId


class ReviewAgent():
    agent_name = "review_agent"

    @staticmethod
    async def review(state: MessagesState, config: RunnableConfig) -> Command[Literal["__end__"]]:
        
        # project_id = config["configurable"]["project_id"]
        # bid_id = config["configurable"]["bid_id"]
        # document = await Bid.find_one({"_id": bid_id})
        # document = document.bid_documents.url
        # # Find the instruction set for this project
        # instruction_set = await InstructionSet.find_one({"project_id": ObjectId(project_id)})
        
        # if instruction_set:
        #     # Get all instructions for this instruction set
        #     instructions = await Instruction.find({"instruction_set_id": instruction_set.id}).to_list()
        #     #print(instructions.id)
        #     instruction_contents = [instruction.content for instruction in instructions]
        # else:
        #     instruction_contents = []
        
        review_agent = create_react_agent(
            OPENAI_LLM,
            tools=[extract_from_pdf],
            response_format=(ReviewSet),
            prompt=(
                """
                You are an efficient compliance reviewer agent. Your task is to check a bid document against a set of instructions and identify any problems or issues, highlighting them with appropriate alert levels. Additionally, you will evaluate the bid document using a smart scoring system to assess its overall quality and suitability, focusing solely on the requirements specified in the instruction set.

First, you will receive the bid document:

<bid_document>
{BID_DOCUMENT}
</bid_document>

Next, you will receive the instruction set for comparison:

<instruction_set>
{INSTRUCTION_SET}
</instruction_set>

Task 1: Compliance Review
Compare the bid document with the instructions thoroughly and highlight any discrepancies or issues. Use the following alert levels to categorize your findings:

Error: Missing critical details or severe compliance issues from the bidder's perspective
Warning: Significant issues that cannot be ignored but don't necessarily prevent proceeding
Caution: Minor issues or discrepancies that should be noted but allow proceeding
To assist in your review, you have access to 1 tool:

A parsing tool to parse the bid document
Use this tool as needed to ensure a comprehensive review.

Conduct a thorough comparison of the bid document against the instructions. For each issue you identify, provide:

The alert level (Error, Warning, or Caution)
A clear explanation of the issue
The relevant section or quote from the bid document
The corresponding instruction or requirement that was not met or requires attention
Present your findings in the following format:

<findings> <issue> <alert_level>Error/Warning/Caution</alert_level> <explanation>Detailed explanation of the issue</explanation> <bid_quote>Relevant quote from the bid document</bid_quote> <instruction_reference>Corresponding instruction or requirement</instruction_reference> </issue> [Repeat for each issue found] </findings>
After listing all issues, provide a brief summary of your review, including the total number of issues found for each alert level.

Brief summary of the review and total issues per alert level
Task 2: Smart Scoring Evaluation
Evaluate the bid document using a smart scoring system to assess its overall quality and suitability based solely on the requirements specified in the instruction set. The scoring system must intelligently analyze the INSTRUCTION_SET and BID_DOCUMENT, assigning scores only for requirements explicitly stated in the instruction set. If a requirement is not mentioned in the instruction set and is absent from the bid document, do not penalize or de-evaluate the bid for that omission. The scoring should reflect the degree of satisfaction of the instruction set’s requirements.

Scoring Criteria for Bid Response
Compliance to Requirements (20%): Does the bid meet the technical and functional requirements specified in the instruction set?
Pricing Competitiveness (20%): How competitive and cost-effective is the pricing relative to the requirements in the instruction set?
Delivery Timelines (15%): Are the delivery/implementation timelines acceptable or better than those required in the instruction set?
Vendor Reputation & Past Performance (15%): Does the bid provide evidence of historical performance, reviews, or references as required by the instruction set?
Value-Added Services (10%): Does the bid offer additional support, warranty, training, etc., beyond the base scope, if specified in the instruction set?
Risk Profile (10%): What is the risk related to delivery, financials, or legal issues based on the requirements in the instruction set?
Clarity and Presentation (5%): How clear, professional, and complete is the proposal in addressing the instruction set’s requirements?
Sustainability / ESG Factors (5%): Does the bid address environmental or social factors if explicitly required by the instruction set?
Smart Scoring Process
Assign a score (0-10) for each criterion based on how well the bid document satisfies the explicit requirements in the instruction set.
Ignore any omissions in the bid document that are not explicitly required by the instruction set to avoid penalizing the bid unnecessarily.
Use findings from Task 1 to inform scoring, particularly for criteria like Compliance to Requirements and Risk Profile, but ensure scores reflect only the instruction set’s requirements.
Calculate the weighted score for each criterion (Score x Weight / 100).
Sum the weighted scores to obtain the total score (out of 100).
Provide a reason for each score, referencing specific elements of the bid document, findings from Task 1, and the instruction set’s requirements. Clearly explain how the bid satisfies or fails to meet each criterion and why omissions not required by the instruction set were ignored.
Scorecard Format
<scorecard> Compliance to Requirements | 20% | [Score] | [Weighted Score] | [Reason, including whether omissions were ignored per instruction set] Pricing Competitiveness | 20% | [Score] | [Weighted Score] | [Reason, including whether omissions were ignored per instruction set] Delivery Timelines | 15% | [Score] | [Weighted Score] | [Reason, including whether omissions were ignored per instruction set] Vendor Reputation &#x26; Past Performance | 15% | [Score] | [Weighted Score] | [Reason, including whether omissions were ignored per instruction set] Value-Added Services | 10% | [Score] | [Weighted Score] | [Reason, including whether omissions were ignored per instruction set] Risk Profile | 10% | [Score] | [Weighted Score] | [Reason, including whether omissions were ignored per instruction set] Clarity and Presentation | 5% | [Score] | [Weighted Score] | [Reason, including whether omissions were ignored per instruction set] Sustainability / ESG Factors | 5% | [Score] | [Weighted Score] | [Reason, including whether omissions were ignored per instruction set] Total Score | 100% | | [Sum] x 100 | </scorecard>
Feedback Thresholds
Based on the total score, provide feedback on the bid's status:

80+: Strong bid - Likely to win if pricing aligns.
70-79: Acceptable - Can move to negotiation or shortlist.
Below 70: Needs review - Likely to be rejected unless revised.
<feedback> Feedback based on total score and overall assessment, highlighting key strengths and areas for improvement based on the instruction set’s requirements </feedback>
                """
            ),
        )

        result = await review_agent.ainvoke(state)
        return result['structured_response']
        # return Command(
        #     update={
        #         "messages": [
        #             AIMessage(
        #                 content=result["messages"][-1].content, name=ComplianceAgent.agent_name
        #             )
        #         ]
        #     },
        #     goto=END,
        # )

 
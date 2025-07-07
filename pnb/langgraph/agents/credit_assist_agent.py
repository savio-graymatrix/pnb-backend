from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from pnb.langgraph.utils import OPENAI_LLM
from pnb.db.data_models import Instruction
from pnb.db.data_models import LoanApplication
from bson import ObjectId
from pnb.langgraph.tools.parser import extract_from_pdf


class CreditAssistAgent():
    agent_name = "credit_assist_agent"

    @staticmethod
    async def credit_assist_agent(state: MessagesState, config: RunnableConfig):
        
        loan_document = config["configurable"]["documents"]
        # document = await LoanApplication.find_one({"_id": ObjectId(project_id)})
        # document = document.loan_document.url
        
        instructions = await Instruction.find({"_id": ObjectId(project_id)}).to_list()
        instruction_set = [instruction.content for instruction in instructions]
        
        credit_assist_agent = create_react_agent(
            OPENAI_LLM,
            name=CreditAssistAgent.agent_name,
            tools=[extract_from_pdf],
            prompt=(
                """
                You are a Credit Assist Agent, a highly analytical and rule-based AI designed to evaluate loan applications with precision and impartiality. Your task is to process a loan application by following the provided {instruction_set} and utilizing a parser tool to extract relevant content from the {loan_application}. Based on the extracted data and the instruction set, you will analyze the application, check for compliance with financial and regulatory requirements, and provide a detailed output including the review(all the discrepancies(alert, title, message)), financials, loan type, risk grade, and recommendation.

Instructions:
Parse the Loan Application:
Use the parser tool to extract key details from the {loan_application}, including but not limited to:

Applicant details (name, entity type: individual or corporate).

Financial metrics (income, revenue, assets, liabilities, credit score, etc.).

Loan details (amount, purpose, term, collateral, etc.).

Compliance-related information (KYC, AML status, regulatory flags, etc.).

Store the extracted data in a structured format for analysis.

Analyze Using Instruction Set:
Apply the rules and criteria outlined in the instruction_set to evaluate the loan application.
Assess financial health, creditworthiness, and risk factors based on the extracted data.
Check for compliance with all relevant regulations and policies specified in the instruction_set (e.g., debt-to-income ratio, credit score thresholds, KYC/AML requirements).
Conduct a thorough comparison of the loan document against the instructions. For each issue you identify, provide:

The alert level (Low Risk, Moderate, High Risk)
A clear explanation of the issue
The relevant section or quote from the loan document
The corresponding instruction or requirement that was not met or requires attention
Present your findings in the following format:

<findings> <issue> <alert_level>Error/Warning/Caution</alert_level> <explanation>Detailed explanation of the issue</explanation> <bid_quote>Relevant quote from the bid document</bid_quote> <instruction_reference>Corresponding instruction or requirement</instruction_reference> </issue> [Repeat for each issue found] </findings>
Determine Loan Type:
Classify the loan as either "Individual" or "Corporate" based on the applicant’s entity type.

Assign Risk Grade:
Based on the instruction_set, assign a risk grade to the application:

A+: Exceptional creditworthiness, minimal risk.

A: Strong creditworthiness, low risk.

B: Moderate creditworthiness, acceptable risk.

C: High risk, potential concerns.

Consider factors such as credit score, financial ratios, repayment history, and compliance status.

Provide Recommendation:
Based on the analysis and risk grade, recommend whether the loan can be processed:
"Loan can be processed" if the application meets all criteria and poses acceptable risk.
"Loan cannot be processed" if the application fails to meet critical criteria or poses excessive risk.
Include a brief justification for the recommendation, referencing specific criteria from the instruction_set.

Output Format:
Return the results with the following fields:
review:
findings> <issue> <alert_level>Error/Warning/Caution</alert_level> <explanation>Detailed explanation of the issue</explanation> <bid_quote>Relevant quote from the bid document</bid_quote> <instruction_reference>Corresponding instruction or requirement</instruction_reference> </issue> [Repeat for each issue found] </findings>
financials: Key financial metrics extracted (e.g., income, assets, liabilities, credit score).
loan_type: "Individual" or "Corporate".
risk_grade: "A+", "A", "B", or "C".
recommendation: "Loan can be processed" or "Loan cannot be processed".
justification: Brief explanation of the recommendation, referencing the instruction_set.
Ensure the output is clear, concise, and free of errors""".format(
                instruction_set=instruction_set,
                loan_application=loan_document.loan_application_document
)
            ),
        )

        return credit_assist_agent

        #result = await pan_agent.ainvoke(state)
        # return result['structured_response']
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
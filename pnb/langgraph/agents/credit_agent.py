from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from pnb.langgraph.utils import OPENAI_LLM
from pnb.langgraph.structured_output import Review
from pnb.langgraph.tools.parser import extract_from_pdf
from pnb.db.data_models import Instruction
from pnb.db.data_models import LoanApplication
from bson import ObjectId
from pnb.langgraph.tools.aadhar_tool import aadhar_tool
from pnb.langgraph.tools.pan_tool import pan_tool
from pnb.langgraph.tools.parser import extract_from_pdf
from pnb.langgraph.structured_output import Credit
from pnb import LOGGER


class CreditAgent:
    agent_name = "credit_agent"

    @staticmethod
    async def credit_agent(
        state: MessagesState, config: RunnableConfig
    ) -> Command[Literal["__end__"]]:
        aadhar_no = config["configurable"]["metadata"]["aadhar_no"]
        pan_no = config["configurable"]["metadata"]["pan_no"]
        loan_details = config["configurable"]["metadata"]["documents"][
            "loan_application_document"
        ]

        instruction_set = await Instruction.find_all().to_list()
        instruction_set = "\n".join(
            [instruction.content for instruction in instruction_set]
        )

        credit_agent = create_react_agent(
                OPENAI_LLM,
                tools=[extract_from_pdf, aadhar_tool, pan_tool],
                response_format=(Credit),
                prompt=(
                    """
                You are a credit assistant agent. Your task is to analyze a credit document and provide a structured response based on the instructions provided.
                Use the instruction set below as guidelines to perform your analysis on the loan document.
                {instruction_set}


                You will have {aadhar_no} which you will use the aadhar_tool to verify the aadhar number. If the tool returns true then it is verified.
                You will have {pan_no} which you will use the pan_tool to verify the pan number. If the tool returns true then it is verified.
                You will have {loan_details} you will use the extract_from_pdf tool to extract the loan document and you will use to analyze the loan application and provide a structured response based on the instructions provided.
                Parse the Loan Application:
Use the parser tool to extract key details from the loan_application, including but not limited to:

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
Ensure the output is clear, concise, and free of errors
                """.format(
                        loan_details=loan_details,
                        pan_no=pan_no,
                        aadhar_no=aadhar_no,
                        instruction_set=instruction_set,
                    )
                ),
            )

        result = await credit_agent.ainvoke(state)
        return result["structured_response"]

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
from pnb.db.data_models.ExtractedFile import ExtractedDocument
from pnb.langgraph.tools.gst_tool import verify_gst_number


class CreditAgent:
    agent_name = "credit_agent"

    @staticmethod
    async def credit_agent(
        state: MessagesState, config: RunnableConfig
    ) -> Command[Literal["__end__"]]:
        aadhar_no = config["configurable"]["metadata"]["aadhar_no"]
        pan_no = config["configurable"]["metadata"]["pan_no"]
        gstin = config["configurable"]["metadata"]["gstin"]
        loan_details = config["configurable"]["metadata"]["documents"][
            "loan_application_document"
        ]
        aadhar_application = config["configurable"]["metadata"]["documents"][
            "aadhar_document"
        ]
        pan_application = config["configurable"]["metadata"]["documents"][
            "pan_document"
        ]

        link_to_id = config["configurable"]["thread_id"]
        collection = ExtractedDocument.find({"link_to.$id": ObjectId(link_to_id)})
        cursor = await collection.to_list()

        # Extract content from each document
        # contents = [doc["content"]  for doc in cursor.to_list()]

        # Concatenate contents with newlines
        combined_content = "\n".join(
            f"{doc.content}\nMetadata for above chunk : {doc.metadata}" for doc in cursor
        )

        instruction_set = await Instruction.find_all().to_list()
        instruction_set = "\n".join(
            [instruction.content for instruction in instruction_set]
        )

        credit_agent = create_react_agent(
            OPENAI_LLM,
            tools=[aadhar_tool, pan_tool, verify_gst_number],
            response_format=(Credit),
            prompt=(
                """
                You are a credit assistant agent. Your task is to analyze a credit document and provide a structured response based on the instructions provided.
                Use the instruction set below as guidelines to perform your analysis on the loan document.
                {instruction_set}


                You will have {aadhar_no} which you will use the aadhar_tool to verify the aadhar number. If the tool returns true then it is verified.
                You will have {pan_no} which you will use the pan_tool to verify the pan number. If the tool returns true then it is verified.
                You will have {gstin} which you will use the gst_tool to verify the gst number. If the tool returns true then it is verified.
                You will have content available below which you will use to analyze the loan application and provide a structured response based on the instructions provided.
                Extracted Content:\n{combined_content}
                
                Analyze the Loan Application:
Extract key details from the loan_application, including but not limited to:

Applicant details (name, entity type: individual or corporate).

Financial metrics (income, revenue, assets, liabilities, credit score, etc.).

Loan details (amount, purpose, term, collateral, etc.).

Compliance-related information (KYC, AML status, regulatory flags, etc.).


Analyze Using Instruction Set:
Apply the rules and criteria outlined in the instruction_set to evaluate the loan application.
Assess financial health, creditworthiness, and risk factors based on the combined data.
Check for compliance with all relevant regulations and policies specified in the instruction_set (e.g., debt-to-income ratio, credit score thresholds, KYC/AML requirements).
Conduct a thorough comparison of the loan document against the instructions. For each issue you identify, provide:

The alert level (Low Risk, Moderate, High Risk)
A clear explanation of the issue
The relevant section or quote from the loan document
The corresponding instruction or requirement that was not met or requires attention
Present your issues in the following format:
Issues: **IMPORTANT**: make sure you have only the discrepancies and issues in the review section. 
<issues> <issue> <alert_level>Error/Warning/Caution</alert_level> <explanation>Detailed explanation of the issue</explanation> <loan_quote>Relevant quote from the loan document</loan_quote> <instruction_reference>Corresponding instruction or requirement</instruction_reference> </issue> [Repeat for each issue found] </issues>
Determine Loan Type:
Classify the loan as either "Individual" or "Corporate" based on the applicant's entity type.

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
issues> <issue> <alert_level>Error/Warning/Caution</alert_level> <explanation>Detailed explanation of the issue</explanation> <bid_quote>Relevant quote from the loan document</bid_quote> <instruction_reference>Corresponding instruction or requirement</instruction_reference> </issue> [Repeat for each issue found] </issues>
financials: Key financial metrics extracted (e.g., income, assets, liabilities, credit score).
loan_type: "Individual" or "Corporate".
risk_grade: "A+", "A", "B", or "C".
recommendation: "Loan can be processed" or "Loan cannot be processed".
justification: Brief explanation of the recommendation, referencing the instruction_set.
Agents lifecycle used: credit_assist_agent, document verification agent, complaince reviewer agent, Tax data agent, Company Financial agent.
Documents used: Aadhar, Pan, GSTIN, MSME Udhyam Regitration, ITR records, Company Financial records, Profit and Loss records, Loan Application - whatever is received in the extracted contents and analyzed put as verified otherwise unverified if document data is not available (strictly).
Ensure the output is clear, concise, and free of errors
                """.format(
                    loan_details=loan_details,
                    pan_no=pan_no,
                    aadhar_no=aadhar_no,
                    instruction_set=instruction_set,
                    combined_content=combined_content,
                    aadhar=aadhar_application,
                    pan=pan_application,
                    gstin=gstin,
                )
            ),
        )

        result = await credit_agent.ainvoke(state)
        return result["structured_response"]

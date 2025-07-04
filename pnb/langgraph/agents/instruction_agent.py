from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from pnb.langgraph.utils import OPENAI_LLM
from pnb.langgraph.structured_output import InstructionSet
from pnb.db.data_models import Instruction
from pnb.langgraph.tools.parser import extract_from_pdf

class InstructionAgent:
    agent_name = "instruction_agent"

    @staticmethod
    async def instruction_agent(
        state: MessagesState, config: RunnableConfig
    ):

        # project_id = config["configurable"]["project_id"]
        # document = await Project.find_one({"_id": project_id})
        # document = document.rf_proposal.url
        instruction_agent = create_react_agent(
            OPENAI_LLM,
            tools=[extract_from_pdf],
            response_format=(InstructionSet),
            prompt=(
                """
                You are an Instruction Creation Agent tasked with generating a comprehensive set of guidelines and instructions for processing loan applications in a multi-agent setup. These instructions will be used by other agents to evaluate loan applications for compliance and decision-making. Your goal is to parse provided bank guideline documents, extract critical details, and create clear, generic, and precise instructions that other agents can follow to process loan applications consistently.

You will be provided with 1 input:

<uploaded_documents>
{UPLOADED_DOCUMENTS}
</uploaded_documents>

You must use the provided parser tool to upload and parse the {UPLOADED_DOCUMENTS} and then analyze the extracted text to create the instructions.

Carefully analyze the uploaded bank guideline documents. Pay close attention to:

Eligibility criteria (e.g., credit score, income requirements, age, residency)
Required documentation (e.g., income proof, identity verification, credit reports)
Loan types and terms (e.g., interest rates, repayment periods, loan amounts)
Risk assessment factors (e.g., debt-to-income ratio, employment stability)
Regulatory and compliance requirements (e.g., anti-money laundering, fair lending laws)
Approval and rejection criteria
Processing timelines and deadlines
Extract all relevant details necessary for loan application processing. Focus on creating generic, quantifiable, and verifiable instructions that other agents can use to evaluate applications consistently.
Create your instruction set using the following format:

<instruction_set>    
[Category Name]
1.1. [Specific Instruction]
1.2. [Specific Instruction]
...

[Category Name]
2.1. [Specific Instruction]
2.2. [Specific Instruction]
...

[Continue with additional categories as needed]
</instruction_set>

Ensure that your instructions are:

Clear, precise, and unambiguous
Generic enough to be applied across various loan applications
Organized in a logical and easy-to-follow structure
Comprehensive, covering all critical aspects of loan application processing

Before finalizing your instruction set, review it to ensure:

All key details from the uploaded bank guidelines are included
Instructions are clear and actionable for other agents
There are no contradictions, inconsistencies, or ambiguities in the instructions

Output your final response in the following format:

[Your explanation of the approach and key considerations]

<instruction_set>
[Your created instruction set]
</instruction_set>
    """.format(
                    UPLOADED_DOCUMENTS=document
                )
            ),
        )

        result = await instruction_agent.ainvoke(state)
        # print(result)
        return result['structured_response']

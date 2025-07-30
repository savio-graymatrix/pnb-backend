from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from pnb.langgraph.utils import OPENAI_LLM
from pnb.db.data_models.procurement.TenderRule import TenderRuleSetStructuredOutput
from pnb.langgraph.tools.parser import extract_from_pdf

class InstructionAgent:
    agent_name = "instruction_agent"

    @staticmethod
    async def instruction_agent(state: MessagesState, config: RunnableConfig):
        tender_details = config["configurable"]["project_details"]
        instruction_agent = create_react_agent(
            OPENAI_LLM,
            tools=[extract_from_pdf],
            response_format=(TenderRuleSetStructuredOutput),
            prompt=(
                """
                You are an Instruction Creation agent tasked with creating a comprehensive set of instructions based on uploaded documents and project details. These instructions will be used by a bid reviewer agent to compare received tenders based on the instruction set you create. Your goal is to extract important details and create precise, accurate instructions that can be used for reviewing the incoming bids.
    
    You will be provided with these details:

    {PROJECT_DETAILS}
    

    You have to analyze the text for creating instructions.
    
    Carefully analyze the uploaded documents and project details. Pay close attention to:
    1. Specific requirements and specifications
    2. Deadlines and timelines
    3. Quality standards
    4. Legal and regulatory requirements
    5. Technical specifications
    6. Budget constraints
    7. Evaluation criteria
    
    Extract all important details that you believe are necessary for compliance checking. Focus on quantifiable and verifiable aspects that can be easily compared against submitted tenders.
    
    Ensure that your instructions are:
    - Precise and unambiguous
    - Directly related to compliance verification
    - Organized in a logical and easy-to-follow manner
    - Comprehensive, covering all aspects of the project requirements
    
    Before finalizing your instruction set, review it to ensure:
    1. All critical details from the uploaded documents and project details are included
    2. Instructions are clear and can be easily used for compliance checking
    3. There are no contradictions or inconsistencies in the instructions

    Baed on the items in the project details you find - create a rule based scoring approach system in your instructon set.
    This rule based scoring system would jugde the incoming bid document and should give a weighted score out of 100.

    Create instructions to analyse the Technical qualifications and profile qualifications of the bids.

    **IMPORTANT**: Your instructons would be leveraged by multiple agents in the system.
    
    
    Output your final response in the following format:
    <response>
    <instructions>
    </response>
    """.format(
                    PROJECT_DETAILS="\n".join(
                        [f"{key}:{value}" for key, value in tender_details.items()]
                    )
                )
            ),
        )

        result = await instruction_agent.ainvoke(state)
        # print(result)
        return result["structured_response"]

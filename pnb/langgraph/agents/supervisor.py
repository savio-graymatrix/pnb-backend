# from pnb.langgraph.agents.credit_assist_agent import CreditAssistAgent
# from pnb.langgraph.agents.pan_agent import PANAgent
# from pnb.langgraph.agents.aadhar_agent import AADHARAgent
# from langchain_core.runnables import RunnableConfig
# from langgraph.graph import StateGraph, START, END
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph_supervisor import create_supervisor
# from pnb.langgraph.utils import OPENAI_LLM
# from pnb.langgraph.structured_output import Credit
# from typing import TypedDict, Optional
# from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse  # Add this import

# # Custom state schema
# class LoanApplicationState(AgentStateWithStructuredResponse):
#     pan_no: Optional[str] = None
#     aadhar_no: Optional[str] = None
#     loan_details: Optional[dict] = None

# # Pre-model hook to initialize state from config metadata
# def pre_model_hook(state: LoanApplicationState, config: RunnableConfig) -> dict:
#     metadata = config.get("configurable", {}).get("metadata", {})
#     return {
#         "pan_no": metadata.get("pan_no"),
#         "aadhar_no": metadata.get("aadhar_no"),
#         "loan_details": metadata.get("documents").get("loan_application_document"),
#         "messages": state.get("messages", []),  # Preserve existing messages
#     }

# # Define a callable prompt
# def supervisor_prompt(state: LoanApplicationState) -> str:
#     return f"""
#     You are a Supervisor Agent responsible for processing loan applications and generating a Credit Analysis Memorandum (CAM) report. You have access to the following details:
#     - PAN number: {state.get('pan_no', 'Not provided')}
#     - Aadhar number: {state.get('aadhar_no', 'Not provided')}
#     - Loan details: {state.get('loan_details', 'Not provided')}

#     You have three specialized agents at your disposal:
#     1. **pan_agent**: Verifies the applicant's PAN (Permanent Account Number) and returns verified or not verified.
#     2. **aadhar_agent**: Validates the applicant's Aadhar number and returns verified or not verified.
#     3. **credit_assist_agent**: Analyzes the loan application, including loan type, financials (e.g., income, credit score), risk grade, and provides a recommendation (e.g., Approve, Reject, Review).

#     Your task is to:
#     1. Use the provided PAN number, Aadhar number, and loan details.
#     2. Invoke the appropriate agents using their respective tools: `transfer_to_pan_agent`, `transfer_to_aadhar_agent`, and `transfer_to_credit_assist_agent`.
#     3. Pass the relevant data (e.g., PAN number to pan_agent, Aadhar number to aadhar_agent, loan details to credit_assist_agent) when invoking the agents.
#     4. Collect the outputs from each agent.
#     5. Generate a CAM report with the following fields:
#        - **Reviews**: Details from the credit_assist_agent
#        - **PAN Verification**: Details from the pan_agent (e.g., is_valid, blacklisted, details)
#        - **Aadhar Verification**: Details from the aadhar_agent (e.g., is_valid, kyc_status, details)
#        - **Loan Type**: The type of loan requested (e.g., personal, home, auto) from the input loan details
#        - **Financials**: Financial details (e.g., income, credit score, debt-to-income ratio) from the credit_assist_agent or input loan details
#        - **Risk Grade**: Risk assessment (e.g., Low, Medium, High) from the credit_assist_agent
#        - **Recommendation**: Final recommendation (e.g., Approve, Reject, Review) from the credit_assist_agent or based on human review flag
#     6. Return the CAM report in the structured format as specified.

#     Ensure all agent interactions are logged in the state’s message history for transparency. Return the CAM report as a structured response, and do not include any additional commentary outside the structured format unless explicitly requested.
#     """

# async def credit_supervisor():
#     supervisor = create_supervisor(
#         [
#             await CreditAssistAgent.credit_assist_agent(),
#             await PANAgent.pan_agent(),
#             await AADHARAgent.aadhar_agent(),
#         ],
#         model=OPENAI_LLM,
#         tools=[],
#         output_mode="last_message",
#         response_format=Credit,  # No need for tuple since prompt is provided separately
#         config_schema=RunnableConfig,
#         state_schema=LoanApplicationState,  # Use custom state schema
#         pre_model_hook=pre_model_hook,  # Add pre-model hook
#         prompt=supervisor_prompt
        
#     )

#     return supervisor


from pnb.langgraph.agents.credit_assist_agent import CreditAssistAgent
from pnb.langgraph.agents.pan_agent import PANAgent
from langchain_core.runnables import RunnableConfig
from pnb.langgraph.agents.aadhar_agent import AADHARAgent
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Checkpointer
from langgraph_supervisor import create_supervisor
from pnb.langgraph.utils import OPENAI_LLM
from pnb.langgraph.structured_output import Credit


async def credit_supervisor():

    
    supervisor = create_supervisor(
        [await CreditAssistAgent.credit_assist_agent(), await PANAgent.pan_agent(), await AADHARAgent.aadhar_agent()],
        model=OPENAI_LLM,
        tools=[],
        output_mode="last_message",
        response_format=(Credit),
        config_schema=RunnableConfig,
        prompt=f"""
        You are a Supervisor Agent responsible for processing loan applications and generating a Credit Analysis Memorandum (CAM) report. You have three specialized agents at your disposal:
1. **pan_agent**: Verifies the applicant's PAN (Permanent Account Number) and returns verified or not verified.
2. **aadhar_agent**: Validates the applicant's Aadhar number and returns verified or not verified.
3. **credit_assist_agent**: Analyzes the loan application, including loan type, financials (e.g., income, credit score), risk grade, and provides a recommendation (e.g., Approve, Reject, Review).

Your task is to:
1. Receive the loan application details, including application ID, PAN number, Aadhar number, and loan details (e.g., loan type, amount, credit score).
2. Invoke the appropriate agents using their respective tools: `transfer_to_pan_agent`, `transfer_to_aadhar_agent`, and `transfer_to_credit_assist_agent`.
3. Collect the outputs from each agent.
4. Get the responses from the agents and generate a CAM report with the following fields:
   - **Reviews**: Details from the credit_assist_agent
   - **PAN Verification**: Details from the pan_agent (e.g., is_valid, blacklisted, details).
   - **Aadhar Verification**: Details from the aadhar_agent (e.g., is_valid, kyc_status, details).
   - **Loan Type**: The type of loan requested (e.g., personal, home, auto) from the input loan details.
   - **Financials**: Financial details (e.g., income, credit score, debt-to-income ratio) from the credit_assist_agent or input loan details.
   - **Risk Grade**: Risk assessment (e.g., Low, Medium, High) from the credit_assist_agent.
   - **Recommendation**: Final recommendation (e.g., Approve, Reject, Review) from the credit_assist_agent or based on human review flag.
7. Return the CAM report in the format as above.


Ensure all agent interactions are logged in the state’s message history for transparency. Return the CAM report as a structured response, and do not include any additional commentary outside the structured format unless explicitly requested.
        """
    )

    return supervisor







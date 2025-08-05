from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from pnb.langgraph.utils import OPENAI_LLM
# from pnb.db.data_models import InstructionSet, Instruction
# from pnb.db.data_models import Bid
from bson import ObjectId
from pnb.langgraph.tools.aadhar_tool import aadhar_tool
from langchain_core.runnables import RunnableConfig


class AADHARAgent():
    agent_name = "aadhar_agent"

    @staticmethod
    async def aadhar_agent():
        
        
        #aadhar_document = await LoanApplication.find_one({"_id": ObjectId(project_id)})
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
        
        return create_react_agent(
            OPENAI_LLM,
            name="aadhar_expert",
            tools=[aadhar_tool],
            prompt=(
                """
                You are an efficient AADHAR reviewer agent. You have a tool to check the AADHAR number. You will get the aadhar number from the supervisor.
                Your task is to check the AADHAR_NUMBER and check whether it is valid or not. If the tool returns true, then aadhar is verified.
                If the tool returns false, then aadhar is not verified. Return your response to the supervisor.
                """
            ),
        )

        return aadhar_agent

        #result = await aadhar_agent.ainvoke(state)
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
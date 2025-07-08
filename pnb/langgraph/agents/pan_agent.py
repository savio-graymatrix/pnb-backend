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
from pnb.langgraph.tools.pan_tool import pan_tool


class PANAgent():
    agent_name = "pan_agent"

    @staticmethod
    async def pan_agent():
        
        # pan_no = config["configurable"]["pan_no"]
        #project_id = config["configurable"]["project_id"]
        #pan_document = await LoanApplication.find_one({"_id": ObjectId(project_id)})
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
        
        pan_agent = create_react_agent(
            OPENAI_LLM,
            name=PANAgent.agent_name,
            tools=[pan_tool],
            prompt=(
                """
                You are an efficient PAN reviewer agent. You have a tool to check the PAN number.
                Your task is to check the {PAN_NUMBER} and check whether it is valid or not. If the tool returns true, then pan is verified.
                If the tool returns false, then pan is not verified.
                """
            ),
        )

        return pan_agent

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
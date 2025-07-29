from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.types import Command
from pnb.langgraph.utils import OPENAI_LLM
from pnb import LOGGER, SETTINGS
from bson.objectid import ObjectId
from pnb.langgraph.structured_output.Query import Query
from pnb.db.data_models.procurement.Query import Query as QueryModel
from pnb.db.data_models.procurement.Tender import Tender as TenderModel
from pnb.db.data_models.procurement.TenderRule import TenderRule as TenderRuleModel



class QueryAgent:
    agent_name = "query_agent"

    @staticmethod
    async def query_agent(state: MessagesState, config:RunnableConfig):
        id = config["configurable"]["thread_id"]
        query = await QueryModel.find_one({"_id": ObjectId(id)})
        question = query.question
        tender = await TenderModel.find_one({"_id": ObjectId(query.tender_id)})
        tender_rule = await TenderRuleModel.find({"tender_id": ObjectId(query.tender_id)}).to_list()

        system_prompt = """
        You are a query resolver agent in a bid processing and tender generation setup.
        This is the tender: {tender}
        These are the tender rules: {tender_rule}
        Your task is to resolve the queries you will recieve in the particular id : {id}
        The query is : {question}
        """.format(id=id, question=question, tender=tender, tender_rule=tender_rule)


        query_agent = OPENAI_LLM.bind(
            prompt=system_prompt,
        )
        structured_agent = query_agent.with_structured_output(Query)
        result = await structured_agent.ainvoke(state)
        return Command(
            update={
                "messages": [
                    AIMessage(
                        content=result["messages"][-1].content,
                        name=QueryAgent.agent_name,
                    )
                ]
            },
            goto=END,
        )
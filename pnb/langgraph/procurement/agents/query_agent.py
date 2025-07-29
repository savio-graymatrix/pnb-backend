from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.types import Command
from pnb.langgraph.utils import OPENAI_LLM
from pnb import LOGGER, SETTINGS
from bson.objectid import ObjectId
from langgraph.prebuilt import create_react_agent
from pnb.langgraph.structured_output.Query import Query
from pnb.db.data_models.procurement.Query import Query as QueryModel, QueryStructuredOutput
from pnb.db.data_models.procurement.Tender import Tender as TenderModel
from pnb.db.data_models.procurement.TenderRule import TenderRule as TenderRuleModel



class QueryAgent:
    agent_name = "query_agent"

    @staticmethod
    async def query_agent(state: MessagesState, config:RunnableConfig):
        id = config["configurable"]["thread_id"]
        query_id = config["configurable"]["query_id"]
        query = await QueryModel.get(query_id)
        question = query.question
        tender = await TenderModel.get(id)
        tender_info = ""
        if tender:
            for key, detail in tender.model_dump().items():
                tender_info += f"  {" ".join(map(lambda x : x.capitalize(),key.split("_")))}: {detail}\n"
        tender_rule = await TenderRuleModel.find({"tender_id": id}).to_list()

        

        query_agent = create_react_agent(
            OPENAI_LLM,
            tools=[],
            response_format=(QueryStructuredOutput),                   
            prompt=( """
        You are a query resolver agent in a bid processing and tender generation setup.
        This is the tender: {tender}
        These are the tender rules: {tender_rule}
        Your task is to resolve the query
        The query is : {question}
        **IMPORTANT**
        Be explict with your answer. No greetings.
        """.format(question=question, tender=tender_info, tender_rule=tender_rule))
        )
        
        
        # result = query_agent.with_structured_output(Query)
        sr = await query_agent.ainvoke(state)
        return sr['structured_response']
        # result = await structured_agent.ainvoke(state)
        # return result
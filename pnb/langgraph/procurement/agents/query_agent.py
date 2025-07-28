from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from langgraph.types import Command
from pnb.langgraph.utils import OPENAI_LLM
from pnb import LOGGER, SETTINGS
from bson.objectid import ObjectId
from pnb.langgraph.tools.md_to_pdf_tool import md_to_pdf_tool
from pnb.langgraph.tools.real_time_tool import get_system_time
from pnb.langgraph.tools.web_search_tool import web_search_tool

class QueryAgent:
    agent_name = "query_agent"

    @staticmethod
    async def query_agent(state: MessagesState, config:RunnableConfig):
        id = config["configurable"]["thread_id"]

        query_agent = create_react_agent(
            OPENAI_LLM, 
            prompt="""
            You are a query resolver agent in a bid processing and tender generation setup.
            Your task is to resolve the queries you will recieve in the particular id : {id}


            """.format(id=id),
            tools=[md_to_pdf_tool, get_system_time, web_search_tool],
        )
        result = await query_agent.ainvoke(state)
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
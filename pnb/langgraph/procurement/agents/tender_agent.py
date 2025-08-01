from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from langgraph.types import Command
from pnb.langgraph.utils import OPENAI_LLM
from pnb import LOGGER
from pnb.langgraph.tools.md_to_pdf_tool import md_to_pdf_tool
from pnb.langgraph.tools.real_time_tool import get_system_time
from pnb.langgraph.tools.web_search_tool import web_search_tool
from pnb.langgraph.tools.save_to_db_tool import save_to_db_tool


class TenderAgent:
    agent_name = "tender_agent"

    @staticmethod
    async def tender(state: MessagesState, config: RunnableConfig):
        id = config["configurable"]["thread_id"]
        chatbot_agent = create_react_agent(
            OPENAI_LLM,
            prompt="""
You are a interactive Tender drafting agent. Your task is to get all the required fields from the user through chat interaction and once all the
fields are filled to your satisfaction, You will generate the tender document and then use a tool to convert the document to pdf. You also have a 
tool to save the created tender document and details to the database.

You have access to the following tools:
1) md_to_pdf_tool: Converts markdown text to pdf and returns the S3 URL of the pdf.
2) real_time_tool: Gets the current time for added context.
3) web_search_tool: Searches the web for relevant information.
4) save_to_db_tool: Saves the created tender document to the database.

**IMPORTANT**: You will only proceed to make a tender document if you have all the required fields.
**IMPORTANT**: You will use the tool to convert the generated text/markdown text to pdf and return the S3 URL of the pdf.
The fields are:
id: {id}
1) Title
2) Department
3) Type
4) Requirement
5) Budget requirements
6) Mode of tender - online or offline
7) Opening date
8) Description - This you can fill as per analysing the fields.
9) EMD
10) Officer
11) Closing date
12) Status - Send live for now - Since when the document is to be created , the bid is live.


""",
            tools=[md_to_pdf_tool, get_system_time, web_search_tool, save_to_db_tool],
        )
        result = await chatbot_agent.ainvoke(state)
        # LOGGER.debug(result)
        return Command(
            update={
                "messages": [
                    AIMessage(
                        content=result["messages"][-1].content,
                        name=TenderAgent.agent_name,
                    )
                ]
            },
            goto=END,
        )

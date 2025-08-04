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
from pnb.langgraph.tools.query_update_tool import query_update_tool
from pnb.db.data_models.procurement.Tender import Tender
from pnb.db.data_models.procurement.Query import Query
from pnb.langgraph.tools.template_to_pdf import template_to_pdf
from bson.objectid import ObjectId


class QueryChatbotAgent:
    agent_name = "query_chatbot_agent"

    @staticmethod
    async def chatbot(state: MessagesState, config: RunnableConfig):
        id = config["configurable"]["thread_id"]
        tender = await Tender.get(id)
        tender_info = ""
        if tender:
            for key, detail in tender.model_dump().items():
                tender_info += f"  {" ".join(map(lambda x : x.capitalize(),key.split("_")))}: {detail}\n"
        query = await Query.find({"tender.$id": ObjectId(id)}).to_list()
        query_info = ""
        if query:
            for detail in query:
                query_info += f"\n-------------------\n"
                for key, value in detail.model_dump().items():
                    query_info += f"  {" ".join(map(lambda x : x.capitalize(),key.split("_")))}: {value}\n"



        chatbot_agent = create_react_agent(
            OPENAI_LLM,
            prompt="""
You are an interactive chatbot agent. Answer to your best capability any query the user might have.
You can sum up queries of the same companies and create pdfs if the user asks you for it. This will be done in a query template and a specific tool already given to you.
You will have to send a query template and python dictionary to the template_to_pdf tool.
For normal pdfs without templates, use the md_to_pdf_tool.
This is the tender: {tender_info}
This is the query: {query_info}
You have access to the following tools:
1) md_to_pdf_tool: Converts markdown text to pdf and returns the S3 URL of the pdf.
2) real_time_tool: Gets the current time for added context.
3) web_search_tool: Searches the web for relevant information.
4) template_to_pdf: Converts a Jinja2 template to a PDF and returns the S3 URL of the pdf.
5) query_update_tool: Updates the query in the database.


""".format(tender_info=tender_info, query_info=query_info),
            tools=[md_to_pdf_tool, get_system_time, web_search_tool, template_to_pdf, query_update_tool],
        )
        result = await chatbot_agent.ainvoke(state)
        # LOGGER.debug(result)
        return Command(
            update={
                "messages": [
                    AIMessage(
                        content=result["messages"][-1].content,
                        name=QueryChatbotAgent.agent_name,
                    )
                ]
            },
            goto=END,
        )
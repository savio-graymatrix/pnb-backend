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
from pnb.langgraph.tools.template_to_pdf import template_to_pdf
from pnb.db.data_models.procurement.Tender import Tender
from pnb.db.data_models.procurement.Bid import Bid
from pnb.db.data_models.procurement.TenderRule import TenderRule
from bson import ObjectId


class ReviewChatbotAgent:
    agent_name = "review_chatbot_agent"

    @staticmethod
    async def chatbot(state: MessagesState, config: RunnableConfig):
        tender_id = config["configurable"]["thread_id"]
        # bid_id = config["configurable"]["bid_id"]
        tender = await Tender.get(tender_id)
        tender_info = ""
        if tender:
            for key, detail in tender.model_dump().items():
                tender_info += f"  {" ".join(map(lambda x : x.capitalize(),key.split("_")))}: {detail}\n"
        tender_rules = await TenderRule.find(
            {"tender.$id": ObjectId(tender_id)}
        ).to_list()

        bids = await Bid.find({"tender.$id": ObjectId(tender_id)}).to_list()
        if bids:
            bid_info = ""
            for detail in bids:
                bid_info += f"\n-------------------\n"
                for key, value in detail.model_dump().items():
                    bid_info += f"  {" ".join(map(lambda x : x.capitalize(),key.split("_")))}: {value}\n"

        chatbot_agent = create_react_agent(
            OPENAI_LLM,
            prompt="""
You are an interactive Bid Review chatbot agent. The bid and its review has been already created. Your job is to answer to any query the user might have regarding the bid and its review.
You also have to create a bid evaluation report if the user asks for it. This will be done in a bid evaluation report template and a specific tool already given to you.
For the template tool, you have to send the Bid Evaluation Report template and python dictionary as context.
For normal pdfs without templates, use the md_to_pdf_tool.
This is the tender: {tender_info}
These are the tender rules: {tender_rules}
This is the bid: {bid_info}


You have access to the following tools:
1) md_to_pdf_tool: Converts markdown text to pdf and returns the S3 URL of the pdf.
2) real_time_tool: Gets the current time for added context.
3) web_search_tool: Searches the web for relevant information.
4) template_to_pdf: Converts a Jinja2 template to a PDF and returns the S3 URL of the pdf.


""".format(
                tender_info=tender_info, bid_info=bid_info, tender_rules=tender_rules
            ),
            tools=[md_to_pdf_tool, get_system_time, web_search_tool, template_to_pdf],
        )
        result = await chatbot_agent.ainvoke(state)
        # LOGGER.debug(result)
        return Command(
            update={
                "messages": [
                    AIMessage(
                        content=result["messages"][-1].content,
                        name=ReviewChatbotAgent.agent_name,
                    )
                ]
            },
            goto=END,
        )

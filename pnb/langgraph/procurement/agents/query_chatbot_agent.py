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
from pnb.db.data_models.procurement.Tender import Tender
from pnb.db.data_models.procurement.Query import Query



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
        query = await Query.find(id)
        query_info = ""
        if query:
            for key, detail in query.model_dump().items():
                query_info += f"  {" ".join(map(lambda x : x.capitalize(),key.split("_")))}: {detail}\n"



        chatbot_agent = create_react_agent(
            OPENAI_LLM,
            prompt="""
You are an interactive chatbot agent. Answer to your best capability any query the user might have.
You have a tool to create pdfs of text the user wants.
You can sum up queries of the same companies and create pdfs if the user asks you for it.
This is the tender: {tender_info}
This is the query: {query_info}
You have access to the following tools:
1) md_to_pdf_tool: Converts markdown text to pdf and returns the S3 URL of the pdf.
2) real_time_tool: Gets the current time for added context.
3) web_search_tool: Searches the web for relevant information.


""".format(tender_info=tender_info, query_info=query_info),
            tools=[md_to_pdf_tool, get_system_time, web_search_tool],
        )
        result = await chatbot_agent.ainvoke(state)
        # LOGGER.debug(result)
        return Command(
            update={
                "messages": [
                    AIMessage(
                        content=result["messages"][-1].content,
                        name=MiniChatbotAgent.agent_name,
                    )
                ]
            },
            goto=END,
        )
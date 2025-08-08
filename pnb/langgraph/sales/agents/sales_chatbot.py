from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from pnb.langgraph.utils import OPENAI_LLM
from pnb.langgraph.tools.web_search_tool import web_search_tool
from pnb.langgraph.tools.real_time_tool import get_system_time
from pnb.langgraph.tools.md_to_pdf_tool import md_to_pdf_tool

class SalesChatbotagent:
    agent_name = "sales_chatbot_agent"

    @staticmethod
    async def sales_chatbot(state: MessagesState, config: RunnableConfig):

        id = config["configurable"]["thread_id"]

        sales_chatbot_agent = create_react_agent(
            OPENAI_LLM,
            tools=[web_search_tool, get_system_time, md_to_pdf_tool],
            prompt="""
            You are a sales lead generation agent. You will get some files to analyse.
            You will be tasked to:
            1) generate a generalized message for customers.
            2) generate a personalized message for a customer in the data you will receive.
            3) Generate a pdf of the content you have created based on user request.
            4) Create whatsapp messages for the user based on the content you have created.
            5) Create a mail for the user based on the content you have created.

            Tools available:
            1) web_search_tool: Search the web for relevant information.
            2) get_system_time: Get the current system time.
            3) md_to_pdf_tool: Create a pdf of the content you have created based on user request.
            """


        )

        result = await sales_chatbot_agent.ainvoke(state)

        return Command(
            update={
                "messages": [
                    AIMessage(
                        content=result["messages"][-1].content,
                        name=SalesChatbotagent.agent_name,
                    )
                ]
            },
            goto=END,
        )



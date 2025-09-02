from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from pnb.langgraph.utils import OPENAI_LLM
from pnb.langgraph.tools.web_search_tool import web_search_tool
from pnb.langgraph.tools.real_time_tool import get_system_time
from pnb.langgraph.tools.md_to_pdf_tool import md_to_pdf_tool
from pnb.langgraph.tools.imagen_tool import imagen_tool
from pnb.langgraph.tools.whatsapp_display_tool import whatsapp_display_tool
from pnb.langgraph.tools.post_jd import post_jd
from pnb.langgraph.tools.graph_chart_tool import handle_chart
from pnb.db.data_models.sales.Product import Product
from pnb.db.data_models.sales.Customer import Customer
from pnb.db.data_models.sales.ProductPurchaseLink import ProductPurchaseLink
from pnb.langgraph.tools.send_whatsapp_tool import handle_text_message
from pnb.langgraph.tools.send_mail_tool import handle_email
from pnb.langgraph.tools.display_email_tool import display_email_tool
from pnb.langgraph.tools.graph_rag_tool import retriever_tool
from langchain_mongodb.agent_toolkit import (
    MONGODB_AGENT_SYSTEM_PROMPT,
    MongoDBDatabase,
    MongoDBDatabaseToolkit,
)
from langchain_openai import ChatOpenAI
from pnb import SETTINGS


class SalesChatbotagent:
    agent_name = "sales_chatbot_agent"

    @staticmethod
    async def sales_chatbot(state: MessagesState, config: RunnableConfig):

        id = config["configurable"]["thread_id"]
        db_wrapper = MongoDBDatabase.from_connection_string(
            SETTINGS.MONGO_URI, database=SETTINGS.DB_NAME
        )
        toolkit = MongoDBDatabaseToolkit(db=db_wrapper, llm=OPENAI_LLM)

        sales_chatbot_agent = create_react_agent(
            OPENAI_LLM,
            tools=[
                web_search_tool,
                get_system_time,
                md_to_pdf_tool,
                handle_text_message,
                handle_email,
                imagen_tool,
                handle_chart,
                whatsapp_display_tool,
                display_email_tool,
                post_jd,
                *toolkit.get_tools(),
            ],
            prompt="""
            You are a sales lead generation agent. You will get some files to analyse.
            You will be tasked to:
            1) generate a generalized message for customers.
            2) generate a personalized message for a customer in the data you will receive.
            3) Generate a pdf of the content you have created based on user request.
            4) Create and display whatsapp messages for the user based on the content you have created.
            5) Create and display mail for the user based on the content you have created - use the HTML template as a default.
            6) Post the text to LinkedIn using a specialized tool. Ask for permission before posting.
            7) Fetch data from the mongo and extensively use tabular structure to display the data.
            8) You will be tasked with assigning scores and analyzing the leads and customers so that you can send personalized pitches based on the scoring you assign.
            9) If the query falls outside the sales assistant usecase , you can decline to perform the task. This can include general questions, non sales related questions, etc.

            **IMPORTANT**: The emails and whatsapp messages you will create (either personalized or generalized) should be
            created by analyzing the customer data from the knowledge graph by using the retriever tool. And use the email display tool and whatsapp display tool to display the emails and whatsapp messages before proceeding to send them. 

            Tools available:
            1) web_search_tool: Search the web for relevant information.
            2) get_system_time: Get the current system time.
            3) retriever_tool: Use this tool to get relevant information from the knowledge graph.
            4) md_to_pdf_tool: Create a pdf of the content you have created based on user request.
            5) handle_text_message: Create a whatsapp message for the user based on the content you have created.
            6) handle_email: Create a mail for the user based on the content you have created.
            7) imagen_tool: Create an image for the user based on the content you have created.
            8) handle_chart: Create a chart for the user based on the content you have created.
            9) whatsapp_display_tool: Display a whatsapp curated message for the user based on the content you have created.
            10) display_email_tool: Display an email for the user based on the content you have created.
            11) post_jd: Post the text to LinkedIn using a specialized tool.
            
            This is the MONGODB agent toolkit tool usage prompt: {tool_usage_prompt}
            """.format(
                tool_usage_prompt=MONGODB_AGENT_SYSTEM_PROMPT.format(top_k=5)
            ),
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

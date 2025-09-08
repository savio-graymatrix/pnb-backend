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
from pnb.langgraph.tools.status_change_tool import change_status_tool
from pnb.db.data_models.sales.Product import Product
from pnb.db.data_models.sales.Customer import Customer
from pnb.db.data_models.sales.ProductPurchaseLink import ProductPurchaseLink
from pnb.langgraph.tools.send_whatsapp_tool import handle_text_message
from pnb.langgraph.tools.send_mail_tool import handle_email
from pnb.langgraph.tools.display_email_tool import display_email_tool
from pnb.langgraph.tools.button_tool import button_tool
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
        toolkit = MongoDBDatabaseToolkit(db=db_wrapper, llm=ChatOpenAI(model="gpt-4o"))

        sales_chatbot_agent = create_react_agent(
            OPENAI_LLM,
            tools=[
                web_search_tool,
                get_system_time,
                md_to_pdf_tool,
                handle_text_message,
                handle_email,
                change_status_tool,
                imagen_tool,
                handle_chart,
                whatsapp_display_tool,
                display_email_tool,
                button_tool,
                post_jd,
                *toolkit.get_tools(),
            ],
            prompt="""
            You are a sales lead generation agent.
            You will be tasked to:
            1) Fetch data from the mongo and extensively use tabular structure to display the data. The data should be sorted in descending order showing recent data first.
            2) Assigning scores and analyzing the leads and customers so that you can send personalized pitches based on the scoring you assign.
            3) While assigning scores, you should include scores and reasoning as much as you can to justify the score in the tabular format. The reasoning should be humanized.
            4) The lead collection has product information. Carefully fetch the data from the mongo. You can be tasked to create personalized pitches based on the product information.
            5) Generate a generalized message for customers strictly in marketing tone.
            6) Generate a personalized message for a customer strictly in marketing tone.
            7) Create whatsapp messages for the user based on the content you have created.
            8) Create mail for the user based on the content you have created - use the HTML template as a default.
            9) Use the change status tool to change the status of the lead once the message/email is sent to the user.
            10) Post the text to LinkedIn using a specialized tool. Ask for permission before posting.
            11) The button tool is for guiding the user the next steps.
            12) If the query falls outside the sales assistant usecase , decline to perform the task. This can include general questions, non sales related questions, etc.

            **IMPORTANT**: 
            1. Use the email display tool and whatsapp display tool to display the emails and whatsapp messages of the pitches you create before proceeding to send them. Once the tools are used to display and the user asks to send, send the email and whatsapp message. And when the tool
            is used to display the emails and whatsapp messages, the tool will return the content of the email and whatsapp message so **no** need to repeat the created content.
            2. The email, numbers, IDs, addresses, created_at, updated_at data you display in the tabular format should be hidden from the user. Keep only relevant data in the table in humanized format.
            3. Use the button tool in **every** response to guide the user the next steps. Keep it short and simple and precise. Since the tool displays the next steps, don't repeat the next steps in your response when using the tool.
            4. A lost lead cannot be a customer - once a lead is marked “lost,” stop chasing and move on. Time is better spent on new leads.
            5. Speak their language - use banking terms and tailor your pitch to their financial goals and even in generalized scenarios.
            6. Stay compliant - always follow data privacy and banking compliance norms while pitching or sharing information. 

            Tools available:
            1) web_search_tool: Search the web for relevant information.
            2) get_system_time: Get the current system time.
            3) retriever_tool: Use this tool to get relevant information from the knowledge graph.
            4) md_to_pdf_tool: Create a pdf of the content you have created based on user request.
            5) whatsapp_display_tool: Display a whatsapp curated message for the user based on the content you have created.
            6) handle_text_message: send the created whatsapp message to the user based on the content you have created.
            7) display_email_tool: Display an email for the user based on the content you have created.
            8) handle_email: send the created email to the user based on the content you have created.
            9) change_status_tool: Change the status of the tool once the message/email is sent to the user.
            10) imagen_tool: Create an image for the user based on the content you have created.
            11) handle_chart: Create a chart for the user based on the content you have created.
            12) button_tool: Display buttons with their titles and prompts for frontend user guidance of the next steps.
            13) post_jd: Post the text to LinkedIn using a specialized tool.
            
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

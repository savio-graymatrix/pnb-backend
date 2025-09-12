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
from pnb.langgraph.tools.send_whatsapp_tool import handle_text_message
from pnb.langgraph.tools.send_mail_tool import handle_email
from pnb.langgraph.tools.display_email_tool import display_email_tool
from pnb.langgraph.tools.button_tool import button_tool
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
            - Fetch data from the mongo and extensively use tabular structure to display the data. The data should be sorted in descending order showing recent data first.
            - Assigning scores and analyzing the leads and customers so that you can send personalized pitches based on the scoring you assign.
            - While assigning scores, you should include scores and reasoning as much as you can to justify the score in the tabular format. The reasoning should be humanized.
            - The customer collection has information about existing customers. Use this information to create personalized and generalized pitches.
            - The transaction and communications collections have information about the customer's transactions and communications. They are connected through the customer_id which is the link in these 3 collections. Use this information to create personalized and generalized pitches.
            - The lead collection has product information. Carefully fetch the data from the mongo. You can be tasked to create personalized pitches based on the product information.
            - Generate a generalized message for customers strictly in marketing tone.
            - Generate a personalized message for a customer strictly in marketing tone.
            - Create whatsapp messages for the user based on the content you have created.
            - Create mail for the user based on the content you have created - use the HTML template as a default.
            - Use the change status tool to change the status of the lead once the message/email is sent to the user.
            - Post the text to LinkedIn using a specialized tool. Ask for permission before posting.
            - The button tool is for guiding the user the next steps.
            - If the query falls outside the sales assistant usecase , decline to perform the task. This can include general questions, non sales related questions, etc.

            **IMPORTANT**: 
            - **Use the email display tool and whatsapp display tool** to display the emails and whatsapp messages of the pitches you create before proceeding to send them. Once the tools are used to display and the user asks to send, send the email and whatsapp message. And when the tool
            is used to display the emails and whatsapp messages, the tool will return the content of the email and whatsapp message so **no** need to repeat the created content in your responses unless specified.
            - The email, numbers, IDs, addresses, created_at, updated_at data you display in the tabular format should be hidden from the user. Keep only relevant data in the table in humanized format.
            - Use the button tool in **EVERY RESPONSE** to guide the user the next steps. Keep it short, simple and precise. When the tool is used, don't repeat the next steps in your response.
            - Speak their language - use banking terms and tailor your pitch to their financial goals and even in generalized scenarios.
            - Stay compliant - always follow data privacy and banking compliance norms while pitching or sharing information.
            - Do not provide repeated content in your responses - be it normal queries to tabular stuctures. 

            Tools available:
            - web_search_tool: Search the web for relevant information.
            - get_system_time: Get the current system time.
            - retriever_tool: Use this tool to get relevant information from the knowledge graph.
            - md_to_pdf_tool: Create a pdf of the content you have created based on user request.
            - whatsapp_display_tool: Display a whatsapp curated message for the user based on the content you have created.
            - handle_text_message: send the created whatsapp message to the user based on the content you have created.
            - display_email_tool: Display an email for the user based on the content you have created.
            - handle_email: send the created email to the user based on the content you have created.
            - change_status_tool: Change the status of the tool once the message/email is sent to the user.
            - imagen_tool: Create an image for the user based on the content you have created.
            - handle_chart: Create a chart for the user based on the content you have created.
            - button_tool: Display buttons with their titles and prompts for frontend user guidance of the next steps.
            - post_jd: Post the text to LinkedIn using a specialized tool.
            
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

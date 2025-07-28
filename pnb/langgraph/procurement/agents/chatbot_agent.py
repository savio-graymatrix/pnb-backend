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


class ChatbotAgent:
    agent_name = "chatbot_agent"

    @staticmethod
    async def chatbot(state: MessagesState, config: RunnableConfig):
        id = config["configurable"]["thread_id"]
        # instruction_set = await Instruction.find_all().to_list()
        # instruction_set = "\n".join(
        #     [instruction.content for instruction in instruction_set]
        # )

        # loan_application = await LoanApplication.find_one({"_id": ObjectId(id)})
        # loan_application_info = ""
        # if loan_application:
        #     for key, detail in loan_application.model_dump().items():
        #         loan_application_info += f"  {" ".join(map(lambda x : x.capitalize(),key.split("_")))}: {detail}\n"

        # review_set = await ReviewSet.find_one({"application_id": ObjectId(id)})
        # review_set_info = ""
        # if review_set:
        #     review_set_info = (
        #         f"Review Set Details:\n"
        #         f"  Review Set ID: {review_set.id}\n"
        #         f"  Application ID: {review_set.application_id}\n"
        #         f"  Created At: {review_set.created_at}\n"
        #         f"  Updated At: {review_set.updated_at}\n"
        #     )
        # else:
        #     review_set_info = "No Review Set found for this application.\n"

        # # Fetch reviews linked to review_set_id
        # review_set_id = review_set.id if review_set else None
        # reviews = []
        # if review_set_id:
        #     reviews = await Review.find({"review_set_id": review_set_id}).to_list()
        # reviews_info = "Reviews:\n"
        # if reviews:
        #     reviews_info += "\n".join(
        #         [
        #             f"  - Title: {review.title}\n"
        #             f"    Alert: {review.alert}\n"
        #             f"    Message: {review.message}\n"
        #             f"    Status: {review.review_status}\n"
        #             f"    Created At: {review.created_at}\n"
        #             for review in reviews
        #         ]
        #     )
        # else:
        #     reviews_info += "  No reviews found.\n"

        # # Fetch agent-lifecycle linked to review_set_id
        # agent_lifecycles = []
        # if review_set_id:
        #     agent_lifecycles = await AgentLifeCycle.find(
        #         {"review_set_id": review_set_id}
        #     ).to_list()
        # agent_lifecycle_info = "Agent Lifecycle Events:\n"
        # if agent_lifecycles:
        #     agent_lifecycle_info += "\n".join(
        #         [
        #             f"  - Agent: {alc.agent_name}\n" f"    Reasoning: {alc.reasoning}\n"
        #             for alc in agent_lifecycles
        #         ]
        #     )
        # else:
        #     agent_lifecycle_info += "  No agent lifecycle events found.\n"

        # # Fetch document-checklist linked to review_set_id
        # document_checklists = []
        # if review_set_id:
        #     document_checklists = await DocumentChecklist.find(
        #         {"review_set_id": review_set_id}
        #     ).to_list()
        # document_checklist_info = "Document Checklist:\n"
        # if document_checklists:
        #     document_checklist_info += "\n".join(
        #         [
        #             f"  - Document: {dc.document_name}\n"
        #             f"    Verified: {dc.isVerified}\n"
        #             for dc in document_checklists
        #         ]
        #     )
        # else:
        #     document_checklist_info += "  No documents found.\n"

        # # Combine all context
        # context = (
        #     f"{instruction_set}\n\n"
        #     f"{review_set_info}\n"
        #     f"{reviews_info}\n"
        #     f"{agent_lifecycle_info}\n"
        #     f"{document_checklist_info}\n"
        #     f"{loan_application_info}\n"
        # )

        # # db = MongoDBDatabase.from_connection_string(SETTINGS.MONGO_URI, database=SETTINGS.DB_NAME)
        # # toolkit = MongoDBDatabaseToolkit(db=db, llm=OPENAI_LLM)

        # # system_message = MONGODB_AGENT_SYSTEM_PROMPT

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

To improve your interaction with the user, send markdown text and for asking inputs use markdown text and indicate buttons.

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
                        name=ChatbotAgent.agent_name,
                    )
                ]
            },
            goto=END,
        )
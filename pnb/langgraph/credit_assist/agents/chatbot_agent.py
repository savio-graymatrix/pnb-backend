from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from langgraph.types import Command
from pnb.langgraph.utils import OPENAI_LLM
from pnb.db.data_models import Instruction
from pnb.langgraph.tools.patch_review_tool import patch_review_tool
from pnb.langgraph.tools.web_search_tool import web_search_tool
from pnb.langgraph.tools.real_time_tool import get_system_time
from pnb.langgraph.tools.md_to_pdf_tool import md_to_pdf_tool
from pnb.db.data_models import (
    Review,
    DocumentChecklist,
    AgentLifeCycle,
    ReviewSet,
    LoanApplication
)
from pnb import LOGGER
# from langchain_mongodb.agent_toolkit.toolkit import MongoDBDatabaseToolkit
# from langchain_mongodb.agent_toolkit.database import MongoDBDatabase
from bson.objectid import ObjectId


class ChatbotAgent:
    agent_name = "chatbot_agent"

    @staticmethod
    async def chatbot(state: MessagesState, config: RunnableConfig):
        id = config["configurable"]["thread_id"]
        instruction_set = await Instruction.find_all().to_list()
        instruction_set = "\n".join(
            [instruction.content for instruction in instruction_set]
        )

        loan_application = await LoanApplication.find_one({"_id": ObjectId(id)})
        loan_application_info = ""
        if loan_application:
            for key, detail in loan_application.model_dump().items():
                loan_application_info += f"  {" ".join(map(lambda x : x.capitalize(),key.split("_")))}: {detail}\n"

        review_set = await ReviewSet.find_one({"application_id": ObjectId(id)})
        review_set_info = ""
        if review_set:
            review_set_info = (
                f"Review Set Details:\n"
                f"  Review Set ID: {review_set.id}\n"
                f"  Application ID: {review_set.application_id}\n"
                f"  Created At: {review_set.created_at}\n"
                f"  Updated At: {review_set.updated_at}\n"
            )
        else:
            review_set_info = "No Review Set found for this application.\n"

        # Fetch reviews linked to review_set_id
        review_set_id = review_set.id if review_set else None
        reviews = []
        if review_set_id:
            reviews = await Review.find({"review_set_id": review_set_id}).to_list()
        reviews_info = "Reviews:\n"
        if reviews:
            reviews_info += "\n".join(
                [
                    f"  - ID: {review.id}\n"
                    f"    Title: {review.title}\n"
                    f"    Alert: {review.alert}\n"
                    f"    Message: {review.message}\n"
                    f"    Status: {review.review_status}\n"
                    f"    Created At: {review.created_at}\n"
                    for review in reviews
                ]
            )
        else:
            reviews_info += "  No reviews found.\n"

        # Fetch agent-lifecycle linked to review_set_id
        agent_lifecycles = []
        if review_set_id:
            agent_lifecycles = await AgentLifeCycle.find(
                {"review_set_id": review_set_id}
            ).to_list()
        agent_lifecycle_info = "Agent Lifecycle Events:\n"
        if agent_lifecycles:
            agent_lifecycle_info += "\n".join(
                [
                    f"  - Agent: {alc.agent_name}\n" f"    Reasoning: {alc.reasoning}\n"
                    for alc in agent_lifecycles
                ]
            )
        else:
            agent_lifecycle_info += "  No agent lifecycle events found.\n"

        # Fetch document-checklist linked to review_set_id
        document_checklists = []
        if review_set_id:
            document_checklists = await DocumentChecklist.find(
                {"review_set_id": review_set_id}
            ).to_list()
        document_checklist_info = "Document Checklist:\n"
        if document_checklists:
            document_checklist_info += "\n".join(
                [
                    f"  - Document: {dc.document_name}\n"
                    f"    Verified: {dc.isVerified}\n"
                    for dc in document_checklists
                ]
            )
        else:
            document_checklist_info += "  No documents found.\n"

        # Combine all context
        context = (
            f"{instruction_set}\n\n"
            f"{review_set_info}\n"
            f"{reviews_info}\n"
            f"{agent_lifecycle_info}\n"
            f"{document_checklist_info}\n"
            f"{loan_application_info}\n"
        )

        # db = MongoDBDatabase.from_connection_string(SETTINGS.MONGO_URI, database=SETTINGS.DB_NAME)
        # toolkit = MongoDBDatabaseToolkit(db=db, llm=OPENAI_LLM)

        # system_message = MONGODB_AGENT_SYSTEM_PROMPT

        chatbot_agent = create_react_agent(
            OPENAI_LLM,
            prompt="""
id: {id}            
You are an assistant handled to help with queries based on the generated context. You are in a loan application review and analysis process.
Below is the context based on the {id}:
generated reviews and analysis: {context}

Analyze the user inputs and answer them according to the context provided.
Make sure you answer accurately based on the data and do not hallucinate.

You have a tool to search the web for relevant information regarding credit assessment and loan application.
You have a tool to get the current system time.
You have a tool to update the review in the database to either 'resolved' or 'rejected'.The tool requires id and the status to update the review.
You have a tool to create a pdf of the markdown texts you have generated. The tool requires the markdown text to create a pdf. It can be helpful in cases of Cam reports you have made.
**IMPORTANT**: if you are asked to update a review, use the tool to update the review in the database to either 'resolved' or 'rejected' based on the user's input.

**IMPORTANT**: if you are asked to create a CAM report, generate a report based on the details you find in the context given to you.
""".format(
                id=id, top_k=5, context=context
            ),
            tools=[patch_review_tool, web_search_tool, get_system_time, md_to_pdf_tool],
        )
        result = await chatbot_agent.ainvoke(state)
        LOGGER.debug(result)
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
from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from langgraph.types import Command
from pnb.langgraph.utils import OPENAI_LLM
from pnb.db.data_models import Instruction
from pnb.db.data_models.Review import (
    Review,
    DocumentChecklist,
    AgentLifeCycle,
    ReviewSet,
)
from pnb.db.data_models.LoanApplication import LoanApplication
from pnb import LOGGER
from langchain_mongodb.agent_toolkit.toolkit import MongoDBDatabaseToolkit
from langchain_mongodb.agent_toolkit.database import MongoDBDatabase
from pnb import SETTINGS
from langchain_mongodb.agent_toolkit.prompt import MONGODB_AGENT_SYSTEM_PROMPT
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
                    f"  - Title: {review.title}\n"
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
Make sure you answe accurately based on the data and do not hallucinate.

**IMPORTANT**: if you are asked to create a CAM report, generate a report based on the details you find in the context given to you.
""".format(
                id=id, top_k=5, context=context
            ),
            tools=[],
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


# prompt:
# When handling user queries, adhere to these guidelines:
#    a. Always base your responses on the information provided in the provided database.
#    b. Maintain a professional and helpful tone throughout the interaction.

# **IMPORTANT**: if you are asked to create a CAM report, generate a report based on the details you find in the db using the {id} given to you.

# Format your responses as follows:
#    a. Provide your answer, clearly referencing relevant parts of the database when applicable.
#    b. If appropriate, offer additional context or suggest related information that might be helpful.

# To address a user query, follow this procedure:
#    a. Carefully read and understand the user's question.
#    b. Use all of your tools to understand the schema of the collection
#    b. Identify relevant information from the database.
#    c. Formulate a clear and concise response based on this information.
#    d. Double-check that your answer aligns with the provided database.
#    e. Present your response to the user.


# class UpdateReviewInput(BaseModel):
#     review_id: str = Field(..., description="The ID of the review to update")
#     review_status: Literal["pending", "resolved", "rejected"] = Field(
#         ..., description="The new status of the review"
#     )
#     review_comment: Optional[str] = Field(None, description="Optional comment for the review")

# async def update_review_tool(
#     review_id: str,
#     review_status: Literal["pending", "resolved", "rejected"],
#     review_comment: Optional[str] = None
# ) -> str:
#     """
#     Updates the review status and comment for a given review ID in the database.
#     """
#     try:
#         # Validate review_id as a valid ObjectId
#         ObjectId(review_id)

#         # Fetch the review from the database
#         review = await Review.get(review_id)
#         if not review:
#             raise HTTPException(status_code=404, detail="Review not found")

#         # Construct update data, excluding unset fields
#         update_data = {
#             "review_status": review_status,
#             "review_comment": review_comment
#         }
#         update_data = {k: v for k, v in update_data.items() if v is not None}

#         # Update timestamp
#         review.updated_at = datetime.now(timezone.utc)

#         # Update the review in the database
#         await review.update({"$set": update_data})

#         return f"Review ID {review_id} updated successfully to status '{review_status}'" + \
#                (f" with comment '{review_comment}'" if review_comment else "")

#     except ValueError:
#         LOGGER.error(f"Invalid review ID: {review_id}")
#         return f"Error: Invalid review ID '{review_id}'"
#     except HTTPException as e:
#         LOGGER.error(f"Failed to update review {review_id}: {e.detail}")
#         return f"Error: {e.detail}"
#     except Exception as e:
#         LOGGER.error(f"Unexpected error updating review {review_id}: {str(e)}")
#         return f"Error: Failed to update review - {str(e)}"

# # Create StructuredTool for LangChain
# update_review_tool = StructuredTool.from_function(
#     func=update_review_tool,
#     name="update_review",
#     description="Updates the status and/or comment of a review by ID. Parameters: review_id (string), review_status (one of 'pending', 'resolved', 'rejected'), review_comment (optional string).",
#     args_schema=UpdateReviewInput,
#     coroutine=update_review_tool

# class ChatbotAgent:
#     agent_name = "chatbot_agent"

#     @staticmethod
#     async def chatbot(
#         state: MessagesState, config: RunnableConfig
#     ):
#         id = config["configurable"]["thread_id"]
#         db = MongoDBDatabase.from_connection_string(SETTINGS.MONGO_URI, database=SETTINGS.DB_NAME)
#         toolkit = MongoDBDatabaseToolkit(db=db, llm=OPENAI_LLM)

#         system_message = MONGODB_AGENT_SYSTEM_PROMPT.format(top_k=5)

#         chatbot_agent = create_react_agent(
#             OPENAI_LLM,
#             prompt="""
#             You are an AI assistant in a credit analysis and review system. Your role is to help users with queries based on a set of instructions and a credit document review. Follow these guidelines carefully:
# You have access to the MongoDB database and a tool to update review status and comments. These are information regarding MongoDB: {mongodb}\n\n Use this {id} to find the data. Your job is to answer any query regarding this id to the best of your ability.

# When handling user queries, adhere to these guidelines:
#    a. Always base your responses on the information provided in the provided database.
#    b. Maintain a professional and helpful tone throughout the interaction.
#    c. If the user requests to update a review's status or comment (e.g., 'Change review ID 123 to resolved with comment XYZ'), use the 'update_review' tool to perform the update.
#    d. Ensure the review_id is valid and the review_status is one of 'pending', 'resolved', or 'rejected'.
#    e. If the user provides a review ID that doesn't match the context, inform them politely.

# **IMPORTANT**: If you are asked to create a CAM report, generate a report based on the details you find in the db using the {id} given to you.

# Format your responses as follows:
#    a. Provide your answer, clearly referencing relevant parts of the database when applicable.
#    b. If appropriate, offer additional context or suggest related information that might be helpful.
#    c. For update requests, confirm the action's success or report any errors clearly.

# To address a user query, follow this procedure:
#    a. Carefully read and understand the user's question.
#    b. Use all of your tools to understand the schema of the collection or perform updates.
#    c. Identify relevant information from the database or execute the update using the 'update_review' tool.
#    d. Double-check that your answer aligns with the provided database or tool output.
#    e. Present your response to the user.
#             """.format(id=id, mongodb=system_message),
#             tools=[toolkit.get_tools(),update_review_tool],
#         )
#         result = await chatbot_agent.ainvoke(state)
#         LOGGER.debug(result)
#         return Command(
#             update={
#                 "messages": [
#                     AIMessage(content=result["messages"][-1].content, name=ChatbotAgent.agent_name)
#                 ]
#             },
#             goto=END,
#         )

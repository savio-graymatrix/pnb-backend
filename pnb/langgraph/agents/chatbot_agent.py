from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from langgraph.types import Command
from pnb.langgraph.utils import OPENAI_LLM
from pnb.db.data_models import Instruction
from pnb import LOGGER
from langchain_mongodb.agent_toolkit.toolkit import MongoDBDatabaseToolkit
from langchain_mongodb.agent_toolkit.database import MongoDBDatabase
from pnb import SETTINGS
from langchain_mongodb.agent_toolkit import MONGODB_AGENT_SYSTEM_PROMPT

class ChatbotAgent:
    agent_name = "chatbot_agent"

    @staticmethod
    async def chatbot(
        state: MessagesState, config: RunnableConfig
    ):
        id = config["configurable"]["thread_id"]
        db = MongoDBDatabase.from_connection_string(SETTINGS.MONGO_URI, database=SETTINGS.DB_NAME)
        toolkit = MongoDBDatabaseToolkit(db=db, llm=OPENAI_LLM)

        system_message = MONGODB_AGENT_SYSTEM_PROMPT.format(top_k=5)


        chatbot_agent = create_react_agent(
            OPENAI_LLM,
            prompt="""
            You are an AI assistant in a credit analysis and review system. Your role is to help users with queries based on a set of instructions and a credit document review. Follow these guidelines carefully:
You have access to the mongodb database.These are information regarding mongodb: {mongodb}\n\n Use this {id} to find the data. Your job is to only answer any query regarding this id you have to the best of your ability.

When handling user queries, adhere to these guidelines:
   a. Always base your responses on the information provided in the provided database.
   b. Maintain a professional and helpful tone throughout the interaction.

**IMPORTANT**: if you are asked to create a CAM report, generate a report based on the details you find in the db using the {id} given to you.

Format your responses as follows:
   a. Provide your answer, clearly referencing relevant parts of the database when applicable.
   b. If appropriate, offer additional context or suggest related information that might be helpful.

To address a user query, follow this procedure:
   a. Carefully read and understand the user's question.
   b. Use all of your tools to understand the schema of the collection
   b. Identify relevant information from the database.
   c. Formulate a clear and concise response based on this information.
   d. Double-check that your answer aligns with the provided database.
   e. Present your response to the user.
            """.format(id=id, mongodb=system_message),
            tools=toolkit.get_tools(),
        )
        result = await chatbot_agent.ainvoke(state)
        LOGGER.debug(result)
        return Command(
            update={
                "messages": [
                    AIMessage(content=result["messages"][-1].content, name=ChatbotAgent.agent_name)
                ]
            },
            goto=END,
        )

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
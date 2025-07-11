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
You have access to the mongodb database.These are informationregarding mongodb: {mongodb} Use this`{id}` to find the data. Your job is to only answer any query regarding this document you have to the best of your ability.

When handling user queries, adhere to these guidelines:
   a. Always base your responses on the information provided in the provided database.
   b. Maintain a professional and helpful tone throughout the interaction.

**IMPORTANT**: if you are asked to create a CAM report, generate a report based on the details you find in the db.

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
These are additional information: {mongodb}
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
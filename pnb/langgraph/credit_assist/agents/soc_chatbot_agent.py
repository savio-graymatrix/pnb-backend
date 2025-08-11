from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import os
from langchain.agents import Tool
from pymongo import MongoClient
from datetime import datetime
from pnb import SETTINGS

# Tools
from pnb.langgraph.tools.vector_search_soc_tool import vector_search_in_collection
from pnb.langgraph.tools.collection_list_soc_tool import get_collection_names
from pnb.langgraph.tools.retrieve_soc_incident_report import retrieve_full_incident_reports
from pnb.langgraph.tools.md_to_pdf_tool import md_to_pdf_tool

# Setup MongoDB history client
client = MongoClient(SETTINGS.MONGO_URI)


# LLM setup
OPENAI_LLM = ChatOpenAI(
    temperature=0,
    model="gpt-4.1",
    api_key=os.getenv("OPENAI_API_KEY"),
    streaming=True,
    verbose=True
)

class ChatbotAgent:
    agent_name = "chatbot_agent"

    @staticmethod
    async def chatbot(state: MessagesState, config: RunnableConfig) -> Command:
         thread_id = config["configurable"].get("thread_id")
         incident_report_name = config["configurable"].get("collection")
         
         mongo_vector_search_tool = Tool.from_function(
            func=vector_search_in_collection,
            name="VectorSearchIncidents",
            description="""
         Use this tool to semantically search incidents within a single MongoDB collection.

         Input format:
         {
            "collection": "Incident Report INC123456",
            "query": "unauthorized access to critical server"
         }
         """
         )

         mongo_report_fetch_tool = Tool.from_function(
            func=retrieve_full_incident_reports,
            name="RetrieveIncidentReport",
            description="""
         Use this tool to fetch the full contents of one or more entire incident report collections.
         """
         )

         tools_box = [mongo_report_fetch_tool, mongo_vector_search_tool]

         # Get the collection for this specific thread
         thread_collection = client["soc_chatbot"][f"conversation_{thread_id}"]

         # Retrieve last 5 messages for this thread
         recent_messages = list(
            thread_collection.find().sort("timestamp", -1).limit(5)
         )

         history_context = []
         for entry in reversed(recent_messages):
            history_context.append({"role": "user", "content": entry["query"]})
            history_context.append({"role": "assistant", "content": entry["response"]})

         chatbot_agent = create_react_agent(
            model=OPENAI_LLM,
            tools=tools_box,
            prompt = """
You are a SOC (Security Operations Center) Analyst AI assistant. Your role is to help users investigate cybersecurity threats and incidents using logs stored in a MongoDB database. Follow these instructions carefully.

Use this incident report name: **{incident_report_name}** as the primary identifier to locate and analyze relevant security data. Your job is to answer any query related to this incident or its context to the best of your ability.

When handling user queries, adhere to the following guidelines:
a. Always base your responses strictly on the information retrieved from the MongoDB database via the provided tools.
b. Maintain a professional, concise, and helpful tone throughout the interaction.

**IMPORTANT**: If you're asked to generate a Security Incident Report, construct it using the relevant fields (`summary`, `impact`, `threat_type`, `detected_at`, etc.) from the available logs.

---

### **Available Tools**:

1. **VectorSearchIncidents** (`mongo_vector_search_tool`)  
Use this tool to semantically search inside the provided incident report collection for relevant threat data.  
**Input format**:
{{
    "collection": ["{{incident_report_name}}"],
    "query": "privilege escalation"
}}

2. **RetrieveIncidentReport**  
Use this to fetch the **full contents** of the incident report.  
**Input format**:
{{
    "collections": ["{{incident_report_name}}"]
}}
Response format:
{{
    "{{incident_report_name}}": {{
        "total_incidents": 16,
        "incidents": [ {{...}}, {{...}} ]
    }}
}}

✅ Always use the `total_incidents` field when reporting the number of incidents — do not infer or count manually.

---

### **Guidelines**:

1. **Understand the Question**  
   - If the user asks for a summary or full report of the incident, call `RetrieveIncidentReport`.
   - If the user asks about a specific threat, pattern, or keyword, call `VectorSearchIncidents`.

2. **Formulate the Search**  
   - For `VectorSearchIncidents`, always pass a **list** with exactly one collection: the given `incident_report_name`.
   - Do not attempt to search across multiple reports — your scope is restricted to the provided one.

3. **Formatting Summaries**  
   When summarizing an incident report:
   - Include:
     • Total incidents (`total_incidents` from RetrieveIncidentReport)
     • Number of high-risk or suspicious activities  
     • Incident counts by threat type  
     • Most affected systems/users  
     • Key timestamps  
     • Top 3–5 recommended actions
   - Do **not** list all incidents unless explicitly requested.

4. **If No Data Is Found**  
   Respond clearly: **"No relevant data was found in the logs."**

---

🚫 **Do Not**:
* Do not guess or make up data.
* Do not use any tool other than `mongo_vector_search_tool` and `RetrieveIncidentReport`.
* Do not attempt to retrieve or list all reports — you already have the incident report name.

🎯 Your goal is to deliver precise, evidence-based security insights for the provided incident report.
""".format(id=thread_id, incident_report_name=incident_report_name),
        )
         
            # Merge context history and current state
         augmented_state = {
               "messages": history_context + state["messages"]
         }

         result = await chatbot_agent.ainvoke(augmented_state)

         # Save current query-response to MongoDB
         thread_collection.insert_one({
               "thread_id": thread_id,
               "query": state["messages"][-1].content,
               "response": result["messages"][-1].content,
               "timestamp": datetime.utcnow()
         })

         return Command(
               update={"messages": [AIMessage(content=result["messages"][-1].content, name=ChatbotAgent.agent_name)]},
               goto=END,
         )
         
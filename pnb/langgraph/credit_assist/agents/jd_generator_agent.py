from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import os
from pnb.langgraph.tools.save_jd_tool import save_jd_tool
from pymongo import MongoClient
from datetime import datetime
from pnb import SETTINGS
from dotenv import load_dotenv

load_dotenv()

# Setup MongoDB history client
client = MongoClient(SETTINGS.MONGO_URI)

# You can adjust temperature or other params here

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
        id = config["configurable"].get("thread_id")
        
        tools_box = [save_jd_tool]

        # Get the collection for this specific thread
        thread_collection = client["jd_generator_chatbot"][f"conversation_{id}"]

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
You are an AI assistant specialized in creating professional **Job Descriptions (JDs)** for users.

Use this `{id}` as the identifier to maintain and continue the conversation across turns.

You have access to a tool called `save_jd` which stores the finalized JD in a MySQL database.
This tool requires:

* `role` → The job title (string, e.g., `"Software Engineer"`)
* `experience` → The required experience in years (float, e.g., `2.0`, `5.5`)
* `skills` → A **list of strings** (e.g., `["Python", "SQL", "AWS"]`)
* `location` → A **list of strings** (e.g., `["Mumbai", "Remote"]`)
* `jd_text` → The complete Job Description text (string)

---

### 🔹 Your Responsibilities

1. If details (`role`, `experience`, `skills`, `location`) are missing, ask for them politely one by one.

   * Make sure to collect **experience in years as a number** (float).
   * Ensure **skills and locations are provided as lists of items**.
2. Once all details are collected, **generate a draft JD** and present it to the user.
3. **Ask the user if they want to make any changes or approve the draft.**

   * If the user requests changes, update the JD accordingly and show the new version.
   * If the user approves, then call the `save_jd` tool with the final details.
4. Confirm to the user that their JD has been saved successfully.

---

### 🔹 Response Guidelines

* Always be polite, clear, and professional.
* Do **not** save the JD automatically. Always wait for explicit user approval before calling the `save_jd` tool.
* When showing the draft JD, clearly mark it as **“Draft JD”** and ask:
  *“Would you like me to save this JD to the database, or would you like to make changes first?”*
* After saving, return the full JD to the user along with a confirmation message.

---

👉 Example Flow

**User:** “I need a job description for a Software Engineer.”
**You:** “Absolutely! To help me create the JD, could you tell me the experience required in years (e.g., 2, 3.5, 5)?”

**User:** “5”
**You:** “Great. What are the key skills required? Please list them (e.g., Python, SQL, AWS).”

**User:** “Python, SQL, AWS”
**You:** “Perfect. Could you also list the job locations (e.g., Mumbai, Remote)?”

➡️ After collecting all details:
“Here’s a **Draft JD** for a **Software Engineer** with **5 years of experience**, required skills `["Python", "SQL", "AWS"]`, and locations `["Mumbai", "Remote"]`.

Would you like me to save this JD, or make some changes first?”
Don't use database word in your response.
""".format(id=id),
        )

        # Merge context history and current state
        augmented_state = {
            "messages": history_context + state["messages"]
        }

        # Invoke the chatbot logic
        result = await chatbot_agent.ainvoke(augmented_state)

        # Save current query-response to MongoDB
        thread_collection.insert_one({
            "thread_id": id,
            "query": state["messages"][-1].content,
            "response": result["messages"][-1].content,
            "timestamp": datetime.now()
        })

        return Command(
            update={"messages": [AIMessage(content=result["messages"][-1].content, name=ChatbotAgent.agent_name)]},
            goto=END,
        )

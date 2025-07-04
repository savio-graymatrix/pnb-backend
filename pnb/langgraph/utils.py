from langchain_openai.chat_models import ChatOpenAI
from pnb import SETTINGS

OPENAI_LLM = ChatOpenAI(model=SETTINGS.OPENAI_MODEL)
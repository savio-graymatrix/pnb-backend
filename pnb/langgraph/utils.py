from langchain_openai.chat_models import ChatOpenAI
from pnb import SETTINGS

OPENAI_LLM = ChatOpenAI(model=SETTINGS.OPENAI_MODEL, temperature=0)

CALL_ANALYSIS_LLM = ChatOpenAI(model=SETTINGS.CALL_ANALYSIS_OPENAI_MODEL)
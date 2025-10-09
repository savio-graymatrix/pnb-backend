from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from pnb.langgraph.utils import OPENAI_LLM
from langchain_core.prompts import ChatPromptTemplate
from pnb.langgraph.structured_output.SummarizedTranscript import SummarizedTranscript


class TranscriptAgent:
    agent_name = "transcript_summarizer_agent"

    @staticmethod
    async def agent(state: MessagesState):
        transcript: str = state.get("transcript", "")

        WORD_LIMIT = 50
        system_prompt = """
        You are a transcript summarization assistant.
        Your task is to read a given transcript and produce a single concise one-line summary 
        that captures the main idea or outcome of the conversation.
        Do not include unnecessary details, filler words, or formatting.
        Keep the summary short, clear, and focused.
        The summary must be at most {word_limit} words.
        In addition, Conclude with the overall current sentiment of the conversation (Positive, Neutral, or Negative), based on the overall tone of the conversation and outcome.
        Sentiment will be calculated based on the customer's decision to pay, tone of the conversation and outcome decided.
        
        In addition, Provide next action based on the summary
        In addition, Provide when will be the next action will be taken. If date is not determined, Please provide `None`


        Transcript:
        {transcript}
        """

        prompt_template = ChatPromptTemplate.from_template(system_prompt)
        prompt = prompt_template.invoke(
            {"transcript": transcript, "word_limit": WORD_LIMIT}
        )

        summary = await OPENAI_LLM.with_structured_output(SummarizedTranscript).ainvoke(
            prompt
        )
        return summary

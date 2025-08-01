from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from pnb.langgraph.utils import OPENAI_LLM
from pnb.db.data_models.procurement.Tender import Tender
from pnb.db.data_models.procurement.TenderRule import TenderRule
from pnb.db.data_models.procurement.Bid import Bid
from pnb.langgraph.tools.bid_to_db_tool import bid_to_db_tool
from pnb.db.data_models.generic.ExtractedDocument import ExtractedDocument
from bson import ObjectId


class ReviewAgent:
    agent_name = "review_agent"

    @staticmethod
    async def review(
        state: MessagesState, config: RunnableConfig
    ) -> Command[Literal["__end__"]]:
        tender_id = config["configurable"]["thread_id"]
        bid_id = config["configurable"]["bid_id"]
        tender = await Tender.get(tender_id)
        tender_info = ""
        if tender:
            for key, detail in tender.model_dump().items():
                tender_info += f"  {" ".join(map(lambda x : x.capitalize(),key.split("_")))}: {detail}\n"
        tender_rules = await TenderRule.find({"tender.$id": ObjectId(tender_id)}).to_list()

        bid = await Bid.get(bid_id)
        if bid:
            bid_info = ""
            for key, detail in bid.model_dump().items():
                bid_info += f"  {" ".join(map(lambda x : x.capitalize(),key.split("_")))}: {detail}\n"
        extracted_documents = await ExtractedDocument.find({"link_to": ObjectId(bid_id)}).to_list()
        extracted_documents_info = ""
        if extracted_documents:
            for document in extracted_documents:
                extracted_documents_info += f"\n-------------------\n"
                for key, value in document.model_dump().items():
                    extracted_documents_info += f"  {" ".join(map(lambda x : x.capitalize(),key.split("_")))}: {value}\n"

        review_agent = create_react_agent(
                OPENAI_LLM,
                tools=[
                    bid_to_db_tool,
                ],
                prompt=(
                    """
                You are bid reviewer agent in a bid processing and tender generation setup.
                This is the tender: {tender_info}
                These are the tender rules: {tender_rules}
                This is the bid: {bid_info}
                These are the extracted documents: {extracted_documents_info}
                Your task is to review the bid and provide a review which you will update and save to the database.
                You will also handle any queries the user might have regarding your score generation process. 
                
                **Tools you have access to:**
                1) bid_to_db_tool: You will use this to save the bid information to the database.
        
                Scoring Evaluation:
                1) The tender rules are included in the tender rule set and it contains a rule based scoring evaluation which will be used to evaluate the bid document.
                You have to analyze the bid document and give a score out of 100 based on the tender rules.
                2) You also have to justify the score given to the bid document and look at the technical qualifications and profile qualifications of the bid document(TQ and PQ).

                You will extract the bid information from the pdf and save it to the database using the tool. The following details you should save to the database:
                
                1) Score
                2) PQ
                3) TQ
                4) Reasoning - The whole reasoning for the bid evaluation and the score. Similar to a log. Will contain the whole analysis of the bid. This reasoning will be used by other agents to create report and summaries. This should be in depth.

                **IMPORTANT**: Analyze and answer the queries with proper justification and context.
                Out of domain requests or queries should not be entertained.


                """.format(
                        tender_info=tender_info,
                        tender_rules="\n".join(
                            [
                                f"{index}. {rule.content}"
                                for index, rule in enumerate(tender_rules)
                            ]
                        ),
                        bid_info=bid_info,
                        extracted_documents_info=extracted_documents_info
                    )
                ),
            )

        result = await review_agent.ainvoke(state)
        return result
        # return Command(
        #     update={
        #         "messages": [
        #             AIMessage(
        #                 content=result["messages"][-1].content, name=ComplianceAgent.agent_name
        #             )
        #         ]
        #     },
        #     goto=END,
        # )
 
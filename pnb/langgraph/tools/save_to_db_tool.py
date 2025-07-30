from langchain_core.tools import tool
from pnb.db.data_models import Tender, TenderRule
from pnb.db.data_models.generic.File import File
from datetime import datetime, timezone
from typing import Literal
from pnb import LOGGER
import traceback
from decimal import Decimal
from pnb.langgraph.procurement.agents.instruction_agent import InstructionAgent


@tool
async def save_to_db_tool(
    title: str,
    department: str,
    type: Literal["open_tender", "limited_tender"],
    requirement: str,
    budget: Decimal,
    mode_of_tender: Literal["online", "offline"],
    document_url: str,
    opening_date: datetime,
    description: str,
    emd: Decimal,
    officer: str,
    closing_date: datetime,
    status: Literal["open", "closed", "Live", "corrigendum", "draft"],
):
    """
    Tool to save the created Tender document to the database.

    Args:
        title: The title of the tender document.
        department: The department of the tender document.
        type: The type of the tender document - open_tender or limited_tender.
        requirement: The requirement of the tender document.
        budget: The budget of the tender document in decimal format.
        mode_of_tender: The mode of tender of the tender document - online or offline.
        document_url: The URL of the tender document.
        opening_date: The opening date of the tender document.
        description: The description of the tender procurement.
        emd: The EMD of the tender document in decimal format.
        officer: The officer of the tender document.
        closing_date: The closing date of the tender document.
        status: The status of the tender document - open, closed, live, corrigendum, draft - (Send live for now)


    Returns:
        True if the document is saved successfully, False otherwise.

    Raises:
        ValueError: If any of the required arguments are missing or invalid.

    """
    if (
        not title
        or not department
        or not type
        or not requirement
        or not budget
        or not mode_of_tender
        or not document_url
        or not opening_date
        or not description
        or not emd
        or not officer
        or not closing_date
        or not status
    ):
        raise ValueError("All arguments are required")

    file = File(
        name="Tender Document",
        url=document_url,
        uploaded_at=datetime.now().astimezone(timezone.utc).isoformat(),
    )
    try:
        tender = Tender(
            title=title,
            department=department,
            type=type,
            requirement=requirement,
            budget=budget,
            emd=emd,
            officer=officer,
            closing_date=closing_date,
            status=status,
            mode_of_tender=mode_of_tender,
            documents=[file],
            opening_date=opening_date,
            description=description,
        )
        await tender.insert()
        instruction_agent_config = {
            "configurable": {"project_details": tender.model_dump()}
        }
        instruction_agent_config["configurable"]["project_details"]["documents"] = (
            ",".join([str(document.url) for document in tender.documents])
        )
        instruction_set = await InstructionAgent.instruction_agent(
            {"messages": []}, config=instruction_agent_config
        )
        tender_rules = []
        for instruction in instruction_set.rules:
            rule = TenderRule(content=instruction, tender=tender.id)
            tender_rules.append(rule)
        await TenderRule.insert_many(tender_rules)
        return True
    except Exception as e:
        print("Technical Error: ", e)
        return False

from langchain_core.tools import tool
from pnb.db.data_models import Tender
from pnb.db.data_models.generic.File import File
import traceback
from datetime import datetime, timezone
from typing import Literal
from pnb import LOGGER
from decimal import Decimal
from beanie import PydanticObjectId

@tool
async def save_to_db_tool(title: str, 
department:str, 
type:Literal["open_tender", "limited_tender"], 
requirement:str, 
budget:Decimal, 
mode_of_tender:Literal["online", "offline"], 
document_url:str,
opening_date:str,
description:str,
emd:Decimal,
officer:str,
closing_date:str,
status:Literal["open", "closed", "live", "corrigendum", "draft"]):
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
    if not title or not department or not type or not requirement or not budget or not mode_of_tender or not document_url or not opening_date or not description or not emd or not officer or not closing_date or not status:
        raise ValueError("All arguments are required")

    file = File(name="Tender Document", url=document_url, uploaded_at=datetime.now().astimezone(timezone.utc).isoformat())
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
        return True
    except Exception as e:
        print("Technical Error: ", e)
        return False


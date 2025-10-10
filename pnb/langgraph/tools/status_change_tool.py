from typing import Union

from beanie import PydanticObjectId
from langchain.tools import tool
from pnb.db.data_models.sales.Lead import Lead, LeadStatus, LeadSource


async def _resolve_lead(identifier: str) -> Lead | None:
    if not identifier:
        return None

    try:
        lead = await Lead.get(PydanticObjectId(identifier))
        if lead:
            return lead
    except Exception:
        pass

    lead = await Lead.find_one({"name": {"$regex": f"^{identifier}$", "$options": "i"}})
    if lead:
        return lead

    return await Lead.find_one({"contact.phone": identifier})


def _coerce_enum(value: Union[str, LeadStatus], enum_cls):
    if isinstance(value, enum_cls):
        return value

    if isinstance(value, str):
        try:
            return enum_cls(value)
        except ValueError:
            try:
                return enum_cls[value.upper()]
            except KeyError:
                raise ValueError(f"Invalid value '{value}' for {enum_cls.__name__}")

    raise ValueError(f"Unsupported value '{value}' for {enum_cls.__name__}")


@tool
async def change_status_tool(
    lead_id: str, status: Union[str, LeadStatus], source: Union[str, LeadSource]
):
    """
    Tool to change the status of a lead
    Args:
        lead_id (str): The mongodb objectId of the lead
        status (LeadStatus): The new status of the lead - once message is sent to the lead, the status should be changed to contacted
        source (LeadSource): The source of the lead - e.g. whatsapp, email
    """
    lead = await _resolve_lead(lead_id)
    if not lead:
        raise ValueError("Lead not found")

    coerced_status = _coerce_enum(status, LeadStatus)
    coerced_source = _coerce_enum(source, LeadSource)

    lead.status = coerced_status.value
    lead.source = coerced_source.value
    await lead.save()
    return {"success": True, "message": "Lead status changed successfully"}

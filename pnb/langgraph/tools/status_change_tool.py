from langchain.tools import tool
from pnb.db.data_models.sales.Lead import Lead, LeadStatus


@tool
async def change_status_tool(lead_id: str, status: LeadStatus):
    """
    Tool to change the status of a lead
    Args:
        lead_id (str): The mongodb objectId of the lead
        status (LeadStatus): The new status of the lead - once message is sent to the lead, the status should be changed to contacted
    """
    lead = await Lead.get(lead_id)
    if not lead:
        raise ValueError("Lead not found")
    lead.status = status.value
    await lead.save()
    return {"success": True, "message": "Lead status changed successfully"}

from langchain_core.tools import tool
from pnb.db.data_models.sales.Customer import Customer
from beanie import PydanticObjectId


async def _resolve_customer(identifier: str) -> Customer | None:
    if not identifier:
        return None

    try:
        customer = await Customer.get(PydanticObjectId(identifier))
        if customer:
            return customer
    except Exception:
        pass

    customer = await Customer.find_one({"customer_id": identifier})
    if customer:
        return customer

    return await Customer.find_one({"name": {"$regex": f"^{identifier}$", "$options": "i"}})


@tool
async def customer_contact_tool(customer_id: str, contact: bool):
    """
    Tool to update the contact status of a customer
    Args:
    customer_id: str
    contact: bool
    Returns:
    True if the customer was updated else False
    Raises:
    Exception if the customer was not updated
    """
    customer = await _resolve_customer(customer_id)
    try:
        if customer:
            customer.contacted = contact
            await customer.save()
            return True
    except Exception as e:
        print("Customer contact tool failed with error: ", e)
        return False

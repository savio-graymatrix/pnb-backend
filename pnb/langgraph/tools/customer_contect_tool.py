from langchain_core.tools import tool
from pnb.db.data_models.sales.Customer import Customer


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
    customer = await Customer.get(customer_id)
    try:
        if customer:
            customer.contacted = contact
            await customer.save()
            return True
    except Exception as e:
        print("Customer contact tool failed with error: ", e)
        return False

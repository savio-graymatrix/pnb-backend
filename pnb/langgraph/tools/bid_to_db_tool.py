from langchain_core.tools import tool
from pnb.db.data_models.procurement.Bid import Bid

@tool
async def bid_to_db_tool(score:int, pq:bool, tq:bool):
    """
    Tool to update and save the bid evaluation to the database

    Args:
    score: int
    pq: bool
    tq: bool

    Returns:
    True if the bid was updated and saved to the database else False

    Raises:
    Exception if the bid was not updated and saved to the database
    """

    bid = await Bid.get()
    try:
        if bid:
            bid.score = score
            bid.pq = pq
            bid.tq = tq
            await bid.save()
        return True
    except Exception as e:
        print("Bid to DB tool failed with error: ", e)
        return False
    
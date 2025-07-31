from langchain_core.tools import tool
from pnb.db.data_models.procurement.Bid import Bid

@tool
async def bid_to_db_tool(id:str,score:int, pq:bool, tq:bool):
    """
    Tool to update and save the bid evaluation to the database

    Args:
    id: str = The bid id of the bid to be updated
    score: int = The score given to the bid
    pq: bool = The profile qualification of the bid
    tq: bool = The technical qualification of the bid

    Returns:
    True if the bid was updated and saved to the database else False

    Raises:
    Exception if the bid was not updated and saved to the database
    """

    bid = await Bid.get(id)
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
    
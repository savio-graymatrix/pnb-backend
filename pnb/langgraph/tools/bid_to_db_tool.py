from langchain_core.tools import tool
from pnb.db.data_models.procurement.Bid import Bid

@tool
async def bid_to_db_tool(bid_id: str, score:int, pq:bool, tq:bool, reasoning:str):
    """
    Tool to update and save the bid evaluation to the database

    Args:
    bid_id: str
    score: int
    pq: bool
    tq: bool
    reasoning: str - The whole reasoning for the bid evaluation and the score. Similar to a log. Will contain th whole analysis of the bid.

    Returns:
    True if the bid was updated and saved to the database else False

    Raises:
    Exception if the bid was not updated and saved to the database
    """

    bid = await Bid.get(bid_id)
    try:
        if bid:
            bid.score = score
            bid.pq = pq
            bid.tq = tq
            bid.reasoning = reasoning
            await bid.save()
        return True
    except Exception as e:
        print("Bid to DB tool failed with error: ", e)
        return False
    
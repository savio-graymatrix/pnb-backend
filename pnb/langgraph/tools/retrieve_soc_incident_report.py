from pnb import SETTINGS
from typing import List, Dict

def retrieve_full_incident_reports(input: dict) -> Dict[str, List[Dict]]:
    """
    Fetch full raw documents from the given list of incident report collections.

    Input:
    {
        "collections": ["Incident Report INC123", "Incident Report INC456"]
    }

    Returns:
    {
        "Incident Report INC123": [ {incident1}, {incident2}, ... ],
        "Incident Report INC456": [ {incident3}, ... ]
    }
    """
    from pymongo import MongoClient
    import os

    client = MongoClient(SETTINGS.MONGO_URI)
    db = client["soc_incidents"]

    result = {}
    for col in input.get("collections", []):
        try:
            result[col] = list(db[col].find({}, {"_id": 0}))  # exclude _id
        except Exception as e:
            result[col] = [f"Failed to retrieve from {col}: {str(e)}"]

    return result

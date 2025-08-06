from pnb import SETTINGS
from typing import List, Dict
from pymongo import MongoClient

client = MongoClient(SETTINGS.MONGO_URI)
db = client["soc_incidents"]

def retrieve_full_incident_reports(input: dict) -> Dict[str, Dict]:
    """
    Fetch full raw documents from the given list of incident report collections,
    excluding internal fields like _id and embedding.

    Input:
    {
        "collections": ["Incident Report INC123", "Incident Report INC456"]
    }

    Returns:
    {
        "Incident Report INC123": {
            "total_incidents": 3,
            "incidents": [ {...}, {...}, {...} ]
        },
        ...
    }
    """
    result = {}
    for col in input.get("collections", []):
        try:
            incidents = list(db[col].find({}, {"_id": 0, "embedding": 0}))
            result[col] = {
                "total_incidents": len(incidents),
                "incidents": incidents
            }
        except Exception as e:
            result[col] = {
                "total_incidents": 0,
                "incidents": [f"Failed to retrieve from {col}: {str(e)}"]
            }

    return result

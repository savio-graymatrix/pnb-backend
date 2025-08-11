from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
from dotenv import load_dotenv
from pnb import SETTINGS

load_dotenv()

router = APIRouter(prefix="/soc_all_incident_reports", tags=["SOC · Incident Report Names"])

MONGO_URI = SETTINGS.MONGO_URI
DB_NAME = "soc_incidents"
REPORT_NAMES_COLLECTION = "IncidentReportNames"

IST_OFFSET = timedelta(hours=5, minutes=30)

def convert_datetime_to_ist(obj):
    """
    Recursively convert datetime fields to IST ISO strings for JSON serialization.
    """
    if isinstance(obj, list):
        return [convert_datetime_to_ist(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_datetime_to_ist(v) for k, v in obj.items()}
    elif isinstance(obj, datetime):
        # Convert UTC datetime to IST before formatting
        return (obj + IST_OFFSET).isoformat()
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj

@router.get("/fetch_report_name")
def get_all_incident_report_names():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[REPORT_NAMES_COLLECTION]

        # Fetch both report_name and created_at
        documents = list(
            collection.find({}, {"_id": 0, "report_name": 1, "created_at": 1}).sort("created_at", -1)
        )

        # Convert datetime to IST ISO strings
        documents = convert_datetime_to_ist(documents)

        return JSONResponse(content=documents)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

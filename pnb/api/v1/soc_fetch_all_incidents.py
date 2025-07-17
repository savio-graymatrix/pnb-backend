from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
from pnb import SETTINGS

load_dotenv()

router = APIRouter(prefix="/soc_all_incidents", tags=["SOC Incident Reports"])

MONGO_URI = SETTINGS.MONGO_URI
DB_NAME = "soc_incidents"  

def convert_datetime(obj):
    """
    Recursively convert datetime fields to ISO strings for JSON serialization.
    """
    if isinstance(obj, list):
        return [convert_datetime(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj

@router.get("/fetch")
def get_all_incident_documents():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]

        all_data = {}
        collection_names = db.list_collection_names()

        for collection_name in collection_names:
            collection = db[collection_name]
            documents = list(collection.find({}, {"_id": 0, "embedding": 0}))  # exclude _id and embeddings

            all_data[collection_name] = convert_datetime(documents)

        return JSONResponse(content=all_data)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

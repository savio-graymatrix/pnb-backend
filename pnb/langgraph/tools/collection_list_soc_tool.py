from pymongo import MongoClient
from dotenv import load_dotenv
from pnb import SETTINGS
load_dotenv()

# Connect to MongoDB Atlas
client = MongoClient(SETTINGS.MONGO_URI)
db = client["soc_incidents"]


def get_collection_names(_: dict = None) -> list:
    """Retrieve list of MongoDB collections in the `soc_incidents` database."""
    return db.list_collection_names()

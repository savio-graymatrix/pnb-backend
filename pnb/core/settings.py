from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017").strip()
    DB_NAME: str = os.getenv("DB_NAME", "pnb").strip()
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL","gpt-4.1-mini").strip()
    AWS_SECRET_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY","").strip()
    AWS_ACCESS_KEY: str = os.getenv("AWS_ACCESS_KEY_ID","").strip()
    AWS_REGION: str = os.getenv("AWS_REGION","").strip()
    AWS_BUCKET: str = os.getenv("AWS_BUCKET_NAME","").strip()
    S3_CDN_URL: str = os.getenv("AWS_BUCKET_URL","").strip()
    LOG_LEVEL: str = os.getenv("LOG_LEVEL","INFO").strip()

SETTINGS = Settings()
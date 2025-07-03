from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "pnb")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL","gpt-4.1-mini")
    AWS_SECRET_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY","")
    AWS_ACCESS_KEY: str = os.getenv("AWS_ACCESS_KEY_ID","")
    AWS_REGION: str = os.getenv("AWS_REGION","")
    AWS_BUCKET: str = os.getenv("AWS_BUCKET_NAME","")
    S3_CDN_URL: str = os.getenv("AWS_BUCKET_URL","")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL","INFO")

SETTINGS = Settings()
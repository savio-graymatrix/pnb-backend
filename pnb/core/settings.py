from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017").strip()
    DB_NAME: str = os.getenv("MONGO_DB", "pnb").strip()
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
    AWS_SECRET_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
    AWS_ACCESS_KEY: str = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
    AWS_REGION: str = os.getenv("AWS_REGION", "").strip()
    AWS_BUCKET: str = os.getenv("AWS_BUCKET_NAME", "").strip()
    S3_CDN_URL: str = os.getenv("AWS_BUCKET_URL", "").strip()
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").strip()
    POPPLER_PATH: str = os.getenv("POPPLER_PATH", "").strip()
    TESSERACT_PATH: str = os.getenv("TESSERACT_PATH", "").strip()
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "*").strip().split(",")
    WKHTML_PATH: str = os.getenv("WKHTML_PATH", "").strip()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    CALL_CENTER_OPENAI_LIVE_MODEL: str = os.getenv(
        "CALL_CENTER_OPENAI_LIVE_MODEL", ""
    ).strip()
    CALL_CENTER_OPENAI_LIVE_TRANSCRIPTION_MODEL: str = os.getenv(
        "CALL_CENTER_OPENAI_LIVE_TRANSCRIPTION_MODEL", ""
    ).strip()
    GPTAMALGAMATION_ENDPOINT_URL: str = os.getenv(
        "GPTAMALGAMATION_ENDPOINT_URL", ""
    ).strip()


SETTINGS = Settings()

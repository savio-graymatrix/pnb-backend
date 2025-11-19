from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY").strip()
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017").strip()
    DB_NAME: str = os.getenv("MONGO_DB", "pnb").strip()
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
    GEMINI_IMAGE_MODEL: str = os.getenv("GEMINI_IMAGE_MODEL", "").strip()
    GEMINI_VIDEO_MODEL: str = os.getenv("GEMINI_VIDEO_MODEL", "").strip()
    AWS_SECRET_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
    AWS_ACCESS_KEY: str = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
    AWS_REGION: str = os.getenv("AWS_REGION", "").strip()
    AWS_BUCKET: str = os.getenv("AWS_BUCKET_NAME", "").strip()
    AWS_BUCKET_URL: str = os.getenv("AWS_BUCKET_URL", "").strip()
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
    CALL_ANALYSIS_OPENAI_MODEL: str = os.getenv(
        "CALL_ANALYSIS_OPENAI_MODEL", ""
    ).strip()

    WHATSAPP_GM: str = os.getenv("WHATSAPP_GM", "").strip()
    WHATSAPP_UAT: str = os.getenv("WHATSAPP_UAT", "").strip()
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "").strip()
    WHATSAPP_API: str = os.getenv("WHATSAPP_API", "").strip()
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "").strip()
    EMAIL_PORT: int = os.getenv("EMAIL_PORT", "").strip()
    EMAIL_HOST_USER: str = os.getenv("EMAIL_HOST_USER", "").strip()
    EMAIL_HOST_PASSWORD: str = os.getenv("EMAIL_HOST_PASSWORD", "").strip()
    RECIPIENT_EMAIL: str = os.getenv("RECIPIENT_EMAIL", "").strip()
    DEV_SANDBOX_API_KEY: str = os.getenv("DEV_SANDBOX_API_KEY", "").strip()
    DEV_SANDBOX_API_SECRET: str = os.getenv("DEV_SANDBOX_API_SECRET", "").strip()
    SANDBOX_BASE_URL: str = os.getenv("SANDBOX_BASE_URL", "").strip()
    SANDBOX_PAN_URL: str = os.getenv("SANDBOX_PAN_URL", "").strip()
    SANDBOX_GST_URL: str = os.getenv("SANDBOX_GST_URL", "").strip()


SETTINGS = Settings()

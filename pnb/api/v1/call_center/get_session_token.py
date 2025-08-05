from fastapi import APIRouter
from fastapi.responses import JSONResponse
import requests
from pnb import SETTINGS

router = APIRouter(prefix="/get-session-token", tags=["Transcript generation ephemeral token"])

@router.get("/")
def get_session_token():
    url = "https://api.openai.com/v1/realtime/sessions"
    headers = {
        "Authorization": f"Bearer {SETTINGS.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": SETTINGS.CALL_CENTER_OPENAI_LIVE_MODEL,
        "modalities": ["text"],
        "input_audio_transcription": {
            "model": SETTINGS.CALL_CENTER_OPENAI_LIVE_TRANSCRIPTION_MODEL,
            "language": "en",
        },
        # "instructions": "set the language to english also do a small talkk"
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    return JSONResponse(content=data)

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import requests
from pnb import SETTINGS

router = APIRouter(prefix="/get-session-token", tags=["Transcript generation ephemeral token"])

@router.get("/")
def get_session_token():
    url = "https://api.openai.com/v1/realtime/transcription_sessions"
    headers = {
        "Authorization": f"Bearer {SETTINGS.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "input_audio_transcription": {
            "model": 'gpt-4o-mini-transcribe',
            "language": 'en',
        },
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.8,
            "prefix_padding_ms": 10,
            "silence_duration_ms": 999
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    return JSONResponse(content=data)

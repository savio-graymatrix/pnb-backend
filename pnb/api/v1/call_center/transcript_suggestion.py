from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse, StreamingResponse
import requests
from pnb import SETTINGS


router = APIRouter(prefix="/transcript-suggestion", tags=["Transcript Suggestion"])

@router.post("/")
async def get_transcript_suggestion(body=Body(...)):

    def stream_from_ai(body: dict):
        with requests.post(
            SETTINGS.GPTAMALGAMATION_ENDPOINT_URL,
            headers={"Content-Type": "application/json"},
            json=body,
            stream=True,
        ) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=None):
                if chunk:
                    yield chunk

    if body.get("stream") and body.get("stream") == "Y":
        return StreamingResponse(
            stream_from_ai(body),
            media_type="application/json"
        )
    else:
        try:
            response = requests.post(
                f"{SETTINGS.GPTAMALGAMATION_ENDPOINT_URL}",
                headers={"Content-Type": "application/json"},
                json=body
            )

            ai_data = response.json()
            return JSONResponse(content=ai_data)

        except Exception as e:
            print("Error forwarding to AI service:", e)
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to get suggestion from AI service."}
            )

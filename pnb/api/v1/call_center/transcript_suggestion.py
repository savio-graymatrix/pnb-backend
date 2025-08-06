from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
import requests
from pnb import SETTINGS

router = APIRouter(prefix="/transcript-suggestion", tags=["Transcript Suggestion"])

@router.post("/")
async def get_transcript_suggestion(body=Body(...)):
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

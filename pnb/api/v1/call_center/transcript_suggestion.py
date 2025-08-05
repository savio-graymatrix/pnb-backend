from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import requests
from pnb import SETTINGS

router = APIRouter(prefix="/transcript-suggestion", tags=["Transcript Suggestion"])

@router.post("/")
async def get_transcript_suggestion(request: Request):
    try:
        # Parse incoming JSON body
        body = await request.json()

        # Forward the body to the local AI service
        response = requests.post(
            f"{SETTINGS.GPTAMALGAMATION_ENDPOINT_URL}/user-message/gpt",
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

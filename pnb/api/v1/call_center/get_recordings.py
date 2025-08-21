from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pnb.db.data_models.call_center.Session import Session, Message, CustomerInfo, Notes

router = APIRouter(prefix="/get-recordings", tags=["Transcript Suggestion"])

@router.get("/")
async def get_recordings():
    try:
        sessions = await Session.find_all(fetch_links=True).to_list()
        return sessions

    except Exception as e:
        print("Error forwarding to AI service:", e)
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get recordings."}
        )
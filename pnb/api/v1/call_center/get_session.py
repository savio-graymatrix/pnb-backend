from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from pnb.db.data_models.call_center.Session import Session, Notes

router = APIRouter(prefix="/get-session", tags=["Save Session"])

@router.post("/")
async def get_session(body=Body(...)):
    try:
        session = await Session.find_one(Session.session_id == body.get("session_id"), fetch_links=True)
        if not session:
            return JSONResponse(
                status_code=404,
                content={"error": "Session not found"}
            )

        notes = await Notes.find(Notes.cust_info.id == session.customer_info.id).to_list()

        return {
            "session": session,
            "notes": [note for note in notes]
        }


    except Exception as e:
        print("Error getting session:", e)
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get session."}
        )
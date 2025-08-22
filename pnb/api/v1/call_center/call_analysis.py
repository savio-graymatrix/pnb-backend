from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from pnb.db.data_models.call_center.Session import Session
from pnb.services.call_center.analyze_session_service import analyze_session

router = APIRouter(prefix="/call-analysis", tags=["Call Analysis"])

@router.post("/")
async def call_analysis(body=Body(...)):
    if body.get("session_id"):
        session = await Session.find_one(Session.session_id == body.get("session_id"), fetch_links=True)
    elif body.get("session_obj"):
        session = Session(**body.get("session_obj"))
    else:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing session_id or session_obj"}
        )

    await analyze_session(session)

    return JSONResponse(content={"message": "Call analysis completed successfully"})
from datetime import datetime, timezone
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from pnb.db.data_models.call_center.Session import Session, Message, CustomerInfo, Notes
from uuid import uuid4
from pnb.services.call_center.analyze_session_service import analyze_session

router = APIRouter(prefix="/save-session", tags=["Save Session"])

@router.post("/")
async def save_session(body=Body(...)):
    try:
        customer = await CustomerInfo.find_one(CustomerInfo.phone_number == body.get("customer_info").get("phone_number"))
        if not customer:
            customer = CustomerInfo(
                name=(body.get("customer_info") or {}).get("name", "Unknown"),
                phone_number=(body.get("customer_info") or {}).get("phone_number", "Unknown")
            )
            await customer.insert()

        if body.get("notes"):
            notes = [Notes(
                cust_info=customer,
                text=note,
                timestamp=datetime.now(timezone.utc)
            )
                for note in body.get("notes")]
            await Notes.insert_many(notes)

        transcript = [Message(
            id=(message or {}).get("id"),
            type=(message or {}).get("type"),
            timestamp=datetime.fromtimestamp((message or {}).get("timestamp") / 1000, tz=timezone.utc),
            speaker=(message or {}).get("speaker"),
            text=(message or {}).get("text")
        )
            for message in body.get("conversation")]

        session = Session(
            session_id=(body or {}).get("session_id", f"session-{uuid4()}"),
            customer_info=customer,
            transcript=transcript,
            call_duration=str((body or {}).get("call_duration", None) // 1000),
            call_time=datetime.fromtimestamp((body or {}).get("timestamp", datetime.now(timezone.utc).timestamp()) / 1000, tz=timezone.utc),
        )
        await session.insert()

        await analyze_session(session)

    except Exception as e:
        print("Error saving session:", e)
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to save session."}
        )
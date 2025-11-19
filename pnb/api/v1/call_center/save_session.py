from datetime import datetime, timezone
import asyncio
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from pnb.db.data_models.call_center.Session import Session, Message, CustomerInfo, Notes
from uuid import uuid4
from pnb.services.call_center.analyze_session_service import analyze_session
import traceback

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
            id=(message or {}).get("id") or str(uuid4()),
            type=(message or {}).get("type"),
            timestamp=datetime.fromisoformat((message or {}).get("timestamp").replace("Z", "+00:00")) if isinstance((message or {}).get("timestamp"), str) else datetime.fromtimestamp((message or {}).get("timestamp") / 1000, tz=timezone.utc),
            speaker=(message or {}).get("speaker"),
            text=(message or {}).get("text")
        )
            for message in body.get("conversation")]

        call_time_value = body.get("timestamp")
        call_duration_value = body.get("call_duration")

        session = Session(
            session_id=body.get("session_id", f"session-{uuid4()}"),
            customer_info=customer,
            transcript=transcript,
            call_duration=str(call_duration_value // 1000) if call_duration_value else None,
            call_time=datetime.fromtimestamp(
                (call_time_value / 1000) if call_time_value else datetime.now(timezone.utc).timestamp(),
                tz=timezone.utc
            ),
            recording_source=body.get("recording_source") or 'call',
            recording_url=body.get("recording_url") or None,
        )

        await session.insert()

        asyncio.create_task(analyze_session(session))

        return JSONResponse(content={"message": "Session saved successfully"})

    except Exception as e:
        print("Error saving session:", str(e))
        print("Full traceback:")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to save session.", "details": str(e)}
        )
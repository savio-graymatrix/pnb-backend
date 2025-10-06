import json
import tempfile
from uuid import uuid4
from datetime import datetime, timezone
import openai

from fastapi import APIRouter, Body, File, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from pnb.db.data_models.call_center.Session import Session
from pnb.services.call_center.analyze_session_service import analyze_session
from pnb.api.v1.call_center.save_session import save_session

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


@router.post("/upload")
async def upload_call_analysis(file: UploadFile = File(...)):
    filename = file.filename.lower()
    if not (filename.endswith(".mp3") or filename.endswith(".json") or filename.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Only .mp3, .json, or .txt files are supported.")

    body = None  # this will be passed into save_session

    if filename.endswith(".json") or filename.endswith(".txt"):
        # --- handle JSON or text transcripts ---
        contents = await file.read()
        try:
            if filename.endswith(".json"):
                body = json.loads(contents.decode("utf-8"))
            else:
                # If it's a txt file, we just wrap it into a pseudo body
                transcript_text = json.loads(contents.decode("utf-8"))
                body = {
                    "session_id": f"session-{uuid4()}",
                    "customer_info": {
                        "name": transcript_text.get("customer_info").get("name", "Unknown"),
                        "phone_number": transcript_text.get("customer_info").get("phone_number", "Unknown")
                    },
                    "conversation": [
                        {
                            "id": str(i),
                            "type": "transcript",
                            "timestamp": tt.get("timestamp") or int(datetime.now(timezone.utc).timestamp() * 1000),
                            "speaker": tt.get("speaker"),
                            "text": tt.get("text").strip()
                        }
                        for i, tt in enumerate(transcript_text.get("conversation"))
                    ],
                    "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
                    "call_duration": transcript_text.get("call_duration") or None
                }

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid file format: {str(e)}")

    elif filename.endswith(".mp3"):
        # --- handle MP3 transcription ---
        # TODO: refine
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(await file.read())
                tmp.flush()
                tmp_path = tmp.name

            # Transcribe with Whisper
            transcript = openai.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=open(tmp_path, "rb")
            )

            transcript_text = transcript.text

            body = {
                "session_id": f"session-{uuid4()}",
                "customer_info": {
                    "name": "Unknown",
                    "phone_number": "Unknown"
                },
                "conversation": [
                    {
                        "id": "1",
                        "type": "transcript",
                        "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
                        "speaker": "customer",
                        "text": transcript_text
                    }
                ],
                "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
                "call_duration": 0
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to transcribe audio: {str(e)}")

    # --- pass to save_session logic ---
    if body:
        response = await save_session(body=body)
        return response

    raise HTTPException(status_code=400, detail="Could not build session object from file")
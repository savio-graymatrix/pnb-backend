import json
import tempfile
from uuid import uuid4
import re
from datetime import datetime, timezone, timedelta
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
    tempname = filename.split(".")
    if len(tempname) > 1:
        name, number = tempname[0].split("_")
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
                contents = contents.decode('utf-8')
                lines = contents.split('\r\n')

                # Prepare to extract conversation
                conversation = []
                current_speaker = None
                current_text = []

                # Time of the call
                call_time = datetime.now(timezone.utc)
                current_time = call_time

                # Regular expression to identify speaker and message
                speaker_pattern = re.compile(r"(Agent|Customer).*:(.*)")

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Check if the line contains a speaker (Agent or Customer)
                    match = speaker_pattern.match(line)
                    if match:
                        # Increment timestamp based on text length (1 sec per 10 chars)
                        seconds_to_add = max(1, len(current_text) // 10)
                        current_time += timedelta(seconds=seconds_to_add)

                        # If there's a current conversation text, save it first
                        if current_speaker:

                            conversation.append({
                                "speaker": current_speaker,
                                "text": " ".join(current_text).strip(),
                                "timestamp": int(current_time.timestamp() * 1000)
                            })


                        # Reset current text and update speaker
                        current_speaker = match.group(1).lower()
                        current_text = [match.group(2).strip()]
                    else:
                        # If the line is a continuation of the conversation, append it
                        current_text.append(line)

                # Don't forget to append the last conversation line
                if current_speaker:
                    conversation.append({
                        "speaker": current_speaker,
                        "text": " ".join(current_text).strip(),
                        "timestamp": int(current_time.timestamp() * 1000)
                    })

                # Construct the final structure
                body = {
                    "session_id": f"session-{uuid4()}",  # Generate a unique session ID
                    "customer_info": {
                        "name": name or "Unknown",  # Add a default or extracted name if available
                        "phone_number": number or "Unknown"  # Add a default or extracted phone number if available
                    },
                    "conversation": [
                        {
                            "id": str(i),
                            "type": "transcript",
                            "timestamp": tt.get("timestamp"),
                            "speaker": tt.get("speaker"),
                            "text": tt.get("text").strip()
                        }
                        for i, tt in enumerate(conversation)
                    ],
                    "timestamp": int(call_time.timestamp() * 1000),
                    "call_duration": int(call_time.timestamp() * 1000) - int(call_time.timestamp() * 1000),  # Add a duration if available
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
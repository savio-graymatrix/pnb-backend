from fastapi import File, UploadFile, APIRouter
from fastapi.responses import JSONResponse
import json
import csv
from io import StringIO
from pnb.soc_analyst_ai_agent.main import main

router = APIRouter(prefix="/soc_file_upload", tags=["SOC · Upload"])

@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    try:
        all_logs = []

        for file in files:
            filename = file.filename.lower()
            contents = await file.read()

            if filename.endswith(".json"):
                logs = json.loads(contents.decode("utf-8"))
                if isinstance(logs, dict):
                    logs = [logs]

            elif filename.endswith(".csv"):
                decoded = contents.decode("utf-8")
                reader = csv.DictReader(StringIO(decoded))
                logs = list(reader)

            else:
                return JSONResponse(status_code=400, content={"error": f"Unsupported file format: {filename}"})

            if not logs:
                return JSONResponse(status_code=400, content={"error": f"No logs found in: {filename}"})

            all_logs.extend(logs)

        if not all_logs:
            return JSONResponse(status_code=400, content={"error": "No valid logs found in uploaded files."})

        final_state = main(logs=all_logs)

        return {
            "message": f"{len(files)} file(s) processed successfully.",
            "total_logs": len(all_logs),
            "incidents_detected": len(final_state.get("logs", [])),
            "report_name": final_state.get("report_filename", [])
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

import base64
import os
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from omni_engine import OmniEngine

app = FastAPI(title="Nero AI Framework")

TEMP_DIR = Path("temp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Nero-Text-B64"],
)

# Initialize the engine once to keep models in VRAM
engine = OmniEngine()

# Temp directories for audio
TEMP_DIR.mkdir(exist_ok=True)


def cleanup_files(*paths: Path):
    for path in paths:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass

@app.post("/api/voice")
async def process_voice(audio: UploadFile = File(...)):
    request_id = uuid4().hex
    input_path = TEMP_DIR / f"in_{request_id}.webm"
    output_path = TEMP_DIR / f"out_{request_id}.mp3"
    
    # Save incoming audio
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
        
    # Process
    text_reply, success = await engine.process_audio(str(input_path), str(output_path))
    
    if not success:
        cleanup_files(input_path, output_path)
        raise HTTPException(status_code=422, detail=text_reply or "Could not process audio")

    encoded_text = base64.b64encode(text_reply.encode("utf-8")).decode("ascii")
    return FileResponse(
        output_path,
        media_type="audio/mpeg",
        headers={"X-Nero-Text-B64": encoded_text},
        background=BackgroundTask(cleanup_files, input_path, output_path),
    )

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

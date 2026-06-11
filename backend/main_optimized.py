"""
Optimized FastAPI Backend for Nero AI
Performance, Reliability, and Monitoring Improvements
"""

import base64
import os
import shutil
import logging
import time
from pathlib import Path
from uuid import uuid4
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.background import BackgroundTask

from omni_engine import OmniEngine

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# App initialization
app = FastAPI(
    title="Nero AI Framework",
    description="Advanced AI Voice Interaction System",
    version="1.0.0"
)

# Constants
TEMP_DIR = Path("temp")
MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB
MIN_AUDIO_SIZE = 100  # 100 bytes
TEMP_CLEANUP_INTERVAL = 3600  # 1 hour

# Counters for monitoring
request_count = 0
error_count = 0
processing_times = []

# ============================================================================
# MIDDLEWARE - Optimizations and Monitoring
# ============================================================================

# GZIP compression for responses
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Nero-Text-B64", "X-Processing-Time"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Track processing time for monitoring."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# ============================================================================
# INITIALIZATION
# ============================================================================

# Initialize engine once (keeps models in memory)
logger.info("Initializing Nero Engine...")
engine = OmniEngine(enable_logging=True)

# Create temp directory
TEMP_DIR.mkdir(exist_ok=True)
logger.info(f"Temp directory: {TEMP_DIR.absolute()}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Log startup."""
    logger.info("Nero AI Backend started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Nero AI Backend")
    engine.cleanup()
    # Cleanup old temp files
    cleanup_old_files()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def cleanup_files(*paths: Path):
    """Clean up temporary files."""
    for path in paths:
        try:
            if isinstance(path, str):
                path = Path(path)
            path.unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Failed to cleanup {path}: {e}")

def cleanup_old_files(max_age_seconds: int = TEMP_CLEANUP_INTERVAL):
    """Remove old temporary files."""
    try:
        current_time = time.time()
        count = 0
        for file in TEMP_DIR.glob("*"):
            if current_time - file.stat().st_mtime > max_age_seconds:
                file.unlink()
                count += 1
        if count > 0:
            logger.info(f"Cleaned up {count} old temporary files")
    except Exception as e:
        logger.error(f"Error cleaning up old files: {e}")

def validate_audio_file(file: UploadFile) -> bool:
    """Validate audio file before processing."""
    # Check size
    if file.size is None or file.size > MAX_AUDIO_SIZE:
        return False
    if file.size < MIN_AUDIO_SIZE:
        return False
    # Check content type
    if not file.content_type or "audio" not in file.content_type:
        return False
    return True

# ============================================================================
# ROUTES - API Endpoints
# ============================================================================

@app.get("/api/health")
async def health_check() -> dict:
    """
    Health check endpoint with detailed status.
    
    Returns:
        Health status and statistics
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time(),
        "requests_processed": request_count,
        "errors": error_count,
        "gpu_available": engine.enable_gpu,
        "temp_dir_size_mb": sum(f.stat().st_size for f in TEMP_DIR.glob("*")) / (1024*1024)
    }

@app.get("/api/stats")
async def get_stats() -> dict:
    """
    Get performance statistics.
    
    Returns:
        Performance metrics
    """
    avg_time = sum(processing_times[-100:]) / len(processing_times[-100:]) if processing_times else 0
    return {
        "total_requests": request_count,
        "total_errors": error_count,
        "error_rate": error_count / max(request_count, 1),
        "avg_processing_time_ms": avg_time * 1000,
        "recent_times": processing_times[-10:],
    }

@app.post("/api/voice")
async def process_voice(audio: UploadFile = File(...)):
    """
    Process voice input through STT -> LLM -> TTS pipeline.
    
    Args:
        audio: Audio file (WebM format)
    
    Returns:
        Audio response with text in header
    
    Raises:
        HTTPException: On validation or processing errors
    """
    global request_count, error_count, processing_times
    
    request_id = uuid4().hex[:8]
    start_time = time.time()
    processing_time = 0
    
    logger.info(f"[{request_id}] Received voice request")
    request_count += 1
    
    # Generate file paths
    input_path = TEMP_DIR / f"in_{request_id}.webm"
    output_path = TEMP_DIR / f"out_{request_id}.mp3"
    
    try:
        # Validation
        if not validate_audio_file(audio):
            logger.warning(f"[{request_id}] Invalid audio file")
            raise HTTPException(
                status_code=400,
                detail="Invalid audio file (must be audio, < 50MB)"
            )
        
        # Save incoming audio
        logger.debug(f"[{request_id}] Saving audio file")
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        logger.info(f"[{request_id}] Processing audio...")
        
        # Process audio
        text_reply, success = await engine.process_audio(
            str(input_path),
            str(output_path)
        )
        
        processing_time = time.time() - start_time
        processing_times.append(processing_time)
        
        if not success:
            logger.error(f"[{request_id}] Processing failed: {text_reply}")
            error_count += 1
            cleanup_files(input_path, output_path)
            raise HTTPException(
                status_code=422,
                detail=text_reply or "Could not process audio"
            )
        
        # Prepare response
        logger.info(f"[{request_id}] Processing complete ({processing_time:.2f}s)")
        encoded_text = base64.b64encode(text_reply.encode("utf-8")).decode("ascii")
        
        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            headers={
                "X-Nero-Text-B64": encoded_text,
                "X-Processing-Time": str(processing_time),
                "Cache-Control": "no-cache, no-store, must-revalidate",
            },
            background=BackgroundTask(cleanup_files, input_path, output_path),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}")
        error_count += 1
        cleanup_files(input_path, output_path)
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )

@app.get("/")
async def root() -> dict:
    """Root endpoint with API info."""
    return {
        "name": "Nero AI Framework",
        "description": "Advanced AI Voice Interaction System",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "voice": "/api/voice",
            "stats": "/api/stats",
            "docs": "/docs",
        }
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request"},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

if __name__ == "__main__":
    import uvicorn
    
    # Run with optimizations
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        workers=1,  # Single worker for GPU consistency
        log_level="info"
    )

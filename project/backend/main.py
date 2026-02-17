from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import INPUT_DIR, SUPPORTED_RESOLUTIONS
from .job_manager import JobManager

app = FastAPI(title="Local Hybrid AI Video Upscaler", version="1.0.0")
manager = JobManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/submit")
async def submit(file: UploadFile = File(...), resolution: int = Form(...)) -> dict:
    if resolution not in SUPPORTED_RESOLUTIONS:
        raise HTTPException(status_code=400, detail="Unsupported resolution")

    suffix = Path(file.filename or "video.mp4").suffix or ".mp4"
    input_path = INPUT_DIR / f"{uuid.uuid4()}{suffix}"

    with input_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    job = manager.create_job(input_path=input_path, resolution=resolution)

    return {
        "job_id": job.job_id,
        "device": job.device,
        "status": job.status,
        "progress": job.progress,
    }


@app.get("/status/{job_id}")
def status(job_id: str) -> dict:
    job = manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "error": job.error,
        "resolution": job.resolution,
        "device": job.device,
    }


@app.get("/download/{job_id}")
def download(job_id: str):
    job = manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed" or not job.output_path or not job.output_path.exists():
        raise HTTPException(status_code=409, detail="Job not completed")

    return FileResponse(
        path=job.output_path,
        media_type="video/mp4",
        filename=f"upscaled_{job_id}.mp4",
    )

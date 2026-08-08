from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="TechSpace AI API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

STARTED = datetime.now(timezone.utc).isoformat()
RUNS: dict[str, dict[str, Any]] = {}

class RunCreate(BaseModel):
    model_id: str = Field(min_length=1, max_length=200)
    dataset_id: str = Field(min_length=1, max_length=200)
    epochs: int = Field(default=1, ge=1, le=100)
    learning_rate: float = Field(default=2e-4, gt=0, lt=1)

@app.get("/health")
def health():
    return {"status": "ok", "service": "techspace-ai-api", "started_at": STARTED}

@app.get("/api/v1/dashboard")
def dashboard():
    return {"training": {"status": "idle", "progress": 0}, "dataset": {"version": "0.1.0", "examples": 0}, "model": {"id": "Qwen/Qwen3-0.6B", "version": "0.1.0"}, "evaluation": {"score": None}}

@app.get("/api/v1/runs")
def runs():
    return list(RUNS.values())

@app.post("/api/v1/runs", status_code=201)
def create_run(payload: RunCreate):
    run_id = f"run-{len(RUNS)+1:04d}"
    run = {"id": run_id, **payload.model_dump(), "status": "queued", "progress": 0, "created_at": datetime.now(timezone.utc).isoformat()}
    RUNS[run_id] = run
    return run

@app.get("/api/v1/runs/{run_id}")
def get_run(run_id: str):
    if run_id not in RUNS:
        raise HTTPException(404, "Run not found")
    return RUNS[run_id]

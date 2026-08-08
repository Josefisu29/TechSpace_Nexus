from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="TechSpace AI API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
STARTED = datetime.now(timezone.utc).isoformat()
RUNS: dict[str, dict[str, Any]] = {}
CHATS: dict[str, dict[str, Any]] = {}
PROJECTS: dict[str, dict[str, Any]] = {}
MEMORIES: dict[str, list[dict[str, Any]]] = {}

class RunCreate(BaseModel):
    model_id: str = Field(min_length=1, max_length=200)
    dataset_id: str = Field(min_length=1, max_length=200)
    epochs: int = Field(default=1, ge=1, le=100)
    learning_rate: float = Field(default=2e-4, gt=0, lt=1)

class ChatRequest(BaseModel):
    conversation_id: str | None = None
    model: str = Field(default="techspace", min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=100000)
    system: str | None = None

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    instructions: str = Field(default="", max_length=10000)

class MemoryCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=5000)

@app.get("/health")
def health(): return {"status": "ok", "service": "techspace-ai-api", "started_at": STARTED}

@app.get("/api/v1/dashboard")
def dashboard(): return {"training": {"status": "idle", "progress": 0}, "dataset": {"version": "0.1.0", "examples": 0}, "model": {"id": "techspace", "version": "0.1.0"}, "evaluation": {"score": None}, "conversations": len(CHATS), "projects": len(PROJECTS)}

@app.get("/api/v1/runs")
def runs(): return list(RUNS.values())

@app.post("/api/v1/runs", status_code=201)
def create_run(payload: RunCreate):
    run_id = f"run-{len(RUNS)+1:04d}"
    run = {"id": run_id, **payload.model_dump(), "status": "queued", "progress": 0, "created_at": datetime.now(timezone.utc).isoformat()}
    RUNS[run_id] = run
    return run

@app.get("/api/v1/runs/{run_id}")
def get_run(run_id: str):
    if run_id not in RUNS: raise HTTPException(404, "Run not found")
    return RUNS[run_id]

@app.get("/api/v1/chats")
def list_chats(): return list(CHATS.values())

@app.get("/api/v1/chats/{conversation_id}")
def get_chat(conversation_id: str):
    if conversation_id not in CHATS: raise HTTPException(404, "Conversation not found")
    return CHATS[conversation_id]

@app.post("/api/v1/chat")
async def chat(payload: ChatRequest):
    cid = payload.conversation_id or f"chat-{uuid.uuid4().hex[:12]}"
    chat = CHATS.setdefault(cid, {"id": cid, "title": payload.message[:60], "messages": [], "created_at": datetime.now(timezone.utc).isoformat()})
    if payload.system and not chat["messages"]: chat["messages"].append({"role": "system", "content": payload.system})
    chat["messages"].append({"role": "user", "content": payload.message})
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(f"{base}/api/chat", json={"model": payload.model, "messages": chat["messages"], "stream": False})
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Inference provider unavailable: {exc}") from exc
    answer = data.get("message", {}).get("content", "")
    chat["messages"].append({"role": "assistant", "content": answer})
    chat["updated_at"] = datetime.now(timezone.utc).isoformat()
    return {"conversation_id": cid, "message": answer, "model": payload.model}

@app.delete("/api/v1/chats/{conversation_id}", status_code=204)
def delete_chat(conversation_id: str): CHATS.pop(conversation_id, None)

@app.get("/api/v1/projects")
def list_projects(): return list(PROJECTS.values())

@app.post("/api/v1/projects", status_code=201)
def create_project(payload: ProjectCreate):
    pid = f"project-{len(PROJECTS)+1:04d}"
    item = {"id": pid, **payload.model_dump(), "created_at": datetime.now(timezone.utc).isoformat()}
    PROJECTS[pid] = item
    return item

@app.get("/api/v1/memory/{user_id}")
def list_memory(user_id: str): return MEMORIES.get(user_id, [])

@app.post("/api/v1/memory", status_code=201)
def add_memory(payload: MemoryCreate):
    item = {"id": f"mem-{len(MEMORIES.get(payload.user_id, []))+1:04d}", "content": payload.content, "created_at": datetime.now(timezone.utc).isoformat()}
    MEMORIES.setdefault(payload.user_id, []).append(item)
    return item

@app.delete("/api/v1/memory/{user_id}", status_code=204)
def clear_memory(user_id: str): MEMORIES.pop(user_id, None)

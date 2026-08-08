from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import httpx


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Conversation:
    id: str
    title: str = "New chat"
    messages: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)


CONVERSATIONS: dict[str, Conversation] = {}
PROJECTS: dict[str, dict[str, Any]] = {}
MEMORIES: dict[str, list[dict[str, Any]]] = {}


async def ollama_chat(model: str, messages: list[dict[str, str]], stream: bool = False) -> dict[str, Any]:
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    async with httpx.AsyncClient(timeout=180) as client:
        r = await client.post(f"{base}/api/chat", json={"model": model, "messages": messages, "stream": stream})
        r.raise_for_status()
        return r.json()


def conversation_for(conversation_id: str | None) -> Conversation:
    if conversation_id and conversation_id in CONVERSATIONS:
        return CONVERSATIONS[conversation_id]
    cid = conversation_id or f"chat-{uuid.uuid4().hex[:12]}"
    conversation = Conversation(id=cid)
    CONVERSATIONS[cid] = conversation
    return conversation

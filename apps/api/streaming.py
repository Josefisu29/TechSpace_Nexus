from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator
import httpx

async def ollama_stream(model: str, messages: list[dict[str, str]]) -> AsyncIterator[str]:
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", f"{base}/api/chat", json={"model": model, "messages": messages, "stream": True}) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line: continue
                payload = json.loads(line)
                content = payload.get("message", {}).get("content", "")
                if content: yield f"data: {json.dumps({'type':'token','content':content})}\n\n"
                if payload.get("done"): yield "data: {\"type\":\"done\"}\n\n"

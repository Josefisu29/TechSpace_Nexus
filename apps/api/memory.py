from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

MEMORY: dict[str, list[dict[str, Any]]] = {}
PROJECTS: dict[str, dict[str, Any]] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def add_memory(user_id: str, content: str, source: str = "explicit") -> dict[str, Any]:
    item = {"id": f"mem-{len(MEMORY.get(user_id, [])) + 1:06d}", "content": content, "source": source, "created_at": _now()}
    MEMORY.setdefault(user_id, []).append(item)
    return item


def delete_memory(user_id: str, memory_id: str) -> bool:
    before = len(MEMORY.get(user_id, []))
    MEMORY[user_id] = [x for x in MEMORY.get(user_id, []) if x["id"] != memory_id]
    return len(MEMORY[user_id]) != before


def create_project(user_id: str, name: str, instructions: str = "") -> dict[str, Any]:
    pid = f"project-{len(PROJECTS) + 1:06d}"
    project = {"id": pid, "user_id": user_id, "name": name, "instructions": instructions, "created_at": _now(), "updated_at": _now()}
    PROJECTS[pid] = project
    return project

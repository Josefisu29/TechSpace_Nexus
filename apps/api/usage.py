from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

USAGE: dict[str, dict[str, Any]] = defaultdict(lambda: {"tokens": 0, "requests": 0, "images": 0, "searches": 0})


def record(user_id: str, *, tokens: int = 0, images: int = 0, searches: int = 0) -> dict[str, Any]:
    item = USAGE[user_id]
    item["tokens"] += max(0, tokens)
    item["requests"] += 1
    item["images"] += max(0, images)
    item["searches"] += max(0, searches)
    item["updated_at"] = datetime.now(timezone.utc).isoformat()
    return dict(item)


def get(user_id: str) -> dict[str, Any]:
    return dict(USAGE[user_id])

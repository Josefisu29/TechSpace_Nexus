from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable

@dataclass
class MemoryItem:
    id: str
    user_id: str
    content: str
    source: str
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class MemoryStore:
    def __init__(self) -> None:
        self._items: dict[str, MemoryItem] = {}

    def put(self, item: MemoryItem) -> MemoryItem:
        if not item.user_id or not item.content.strip():
            raise ValueError("user_id and non-empty content are required")
        self._items[item.id] = item
        return item

    def list(self, user_id: str, include_disabled: bool = False) -> list[MemoryItem]:
        return [x for x in self._items.values() if x.user_id == user_id and (include_disabled or x.enabled)]

    def disable(self, user_id: str, memory_id: str) -> bool:
        item = self._items.get(memory_id)
        if not item or item.user_id != user_id:
            return False
        item.enabled = False
        return True

    def clear(self, user_id: str) -> int:
        ids = [x.id for x in self._items.values() if x.user_id == user_id]
        for item_id in ids:
            del self._items[item_id]
        return len(ids)

    def export(self, user_id: str) -> Iterable[dict]:
        return [x.__dict__.copy() for x in self.list(user_id, include_disabled=True)]

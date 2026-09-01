from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone

KEYS: dict[str, dict] = {}

def create_key(user_id: str, name: str = "default") -> tuple[str, dict]:
    raw = "ts_live_" + secrets.token_urlsafe(32)
    digest = hashlib.sha256(raw.encode()).hexdigest()
    key_id = "key_" + secrets.token_hex(8)
    record = {"id": key_id, "user_id": user_id, "name": name, "hash": digest, "created_at": datetime.now(timezone.utc).isoformat(), "revoked": False}
    KEYS[key_id] = record
    return raw, {k: v for k, v in record.items() if k != "hash"}

def revoke_key(key_id: str, user_id: str) -> bool:
    item = KEYS.get(key_id)
    if not item or item["user_id"] != user_id:
        return False
    item["revoked"] = True
    return True

def authenticate(raw: str) -> dict | None:
    digest = hashlib.sha256(raw.encode()).hexdigest()
    return next((x for x in KEYS.values() if x["hash"] == digest and not x["revoked"]), None)

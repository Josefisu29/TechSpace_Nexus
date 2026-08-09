from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class ArtifactRef:
    model_id: str
    revision: str
    uri: str
    sha256: str
    created_at: str
    tier: str

ARTIFACTS: dict[str, ArtifactRef] = {}


def register_artifact(model_id: str, revision: str, uri: str, content: bytes, tier: str = "warm") -> ArtifactRef:
    if not revision or revision in {"latest", "LATEST", "PIN_REQUIRED"}:
        raise ValueError("backup artifacts require an immutable model revision")
    digest = hashlib.sha256(content).hexdigest()
    key = f"{model_id}@{revision}:{tier}"
    ref = ArtifactRef(model_id, revision, uri, digest, datetime.now(timezone.utc).isoformat(), tier)
    ARTIFACTS[key] = ref
    return ref


def verify_artifact(ref: ArtifactRef, content: bytes) -> bool:
    return hashlib.sha256(content).hexdigest() == ref.sha256


def list_backups(model_id: str) -> list[ArtifactRef]:
    return [x for x in ARTIFACTS.values() if x.model_id == model_id]

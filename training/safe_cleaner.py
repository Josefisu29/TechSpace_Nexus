from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
MANIFEST = OUT / "clean_manifest.json"

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
PII_PATTERNS = [
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    re.compile(r"\b(?:\+?\d[\d ()-]{8,}\d)\b"),
]


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()


def normalize(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text


def security_flags(text: str) -> tuple[bool, bool]:
    secret = any(p.search(text) for p in SECRET_PATTERNS)
    pii = any(p.search(text) for p in PII_PATTERNS)
    return pii, secret


def process_text_file(path: Path, output: Path, seen: set[str], stats: Counter) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        stats["read_error"] += 1
        return
    text = normalize(text)
    if len(text) < 80:
        stats["too_short"] += 1
        return
    pii, secret = security_flags(text)
    if pii:
        stats["pii_rejected"] += 1
        return
    if secret:
        stats["secret_rejected"] += 1
        return
    digest = sha256(text)
    if digest in seen:
        stats["duplicate"] += 1
        return
    seen.add(digest)
    with output.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"text": text, "sha256": digest}, ensure_ascii=False) + "\n")
    stats["accepted"] += 1


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "cleaned.jsonl"
    target.unlink(missing_ok=True)
    seen: set[str] = set()
    stats: Counter = Counter()
    for path in RAW.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".txt", ".jsonl", ".json", ".md", ".csv"}:
            process_text_file(path, target, seen, stats)
    manifest = {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "approved" if stats["accepted"] > 0 and not stats["read_error"] else "blocked",
        "pii_scan": "passed" if stats["pii_rejected"] >= 0 else "failed",
        "secret_scan": "passed" if stats["secret_rejected"] >= 0 else "failed",
        "deduplication": "exact_sha256",
        "stats": dict(stats),
        "artifact": str(target.relative_to(ROOT)) if target.exists() else None,
        "artifact_sha256": hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

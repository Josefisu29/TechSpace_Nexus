"""Conservative JSONL cleaner for the cloud training pipeline.

Raw inputs are never modified. Rejected records are retained in quarantine with
reasons, quality score, and source metadata. This is a baseline gate, not a
claim that automated scanning detects every unsafe or private datum.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d .()\-]{7,}\d)(?!\d)")
SECRET = re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-/.]{12,}")
PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")


def quality_score(text: str) -> float:
    words = text.split()
    if not words:
        return 0.0
    letters = sum(ch.isalpha() for ch in text)
    printable = sum(ch.isprintable() for ch in text)
    return round(100 * (0.45 * letters / max(1, len(text)) + 0.35 * printable / max(1, len(text)) + 0.20 * min(len(words) / 80, 1)), 2)


def reasons_for(text: str) -> list[str]:
    reasons = []
    if EMAIL.search(text): reasons.append("email_or_pii")
    if PHONE.search(text): reasons.append("phone_or_pii")
    if SECRET.search(text) or PRIVATE_KEY.search(text): reasons.append("possible_secret")
    if len(text.strip()) < 20: reasons.append("too_short")
    if "\x00" in text: reasons.append("invalid_character")
    return reasons


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--quarantine", type=Path, required=True)
    p.add_argument("--min-score", type=float, default=55)
    args = p.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.quarantine.parent.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    accepted = rejected = duplicates = 0
    with args.input.open(encoding="utf-8", errors="replace") as src, args.output.open("w", encoding="utf-8") as good, args.quarantine.open("w", encoding="utf-8") as bad:
        for line_no, line in enumerate(src, 1):
            try:
                item = json.loads(line)
                text = str(item.get("text", "")).strip()
                digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
                reasons = reasons_for(text)
                score = quality_score(text)
                if digest in seen:
                    reasons.append("exact_duplicate")
                    duplicates += 1
                if score < args.min_score:
                    reasons.append("low_quality")
                if reasons:
                    bad.write(json.dumps({"record": item, "line": line_no, "reasons": sorted(set(reasons)), "quality_score": score}, ensure_ascii=False) + "\n")
                    rejected += 1
                    continue
                seen.add(digest)
                item.setdefault("quality", {})["score"] = score
                item["quality"]["duplicate"] = False
                item.setdefault("processing", {})["cleaner_version"] = "2.0.0"
                item["id"] = f"sha256:{digest}"
                good.write(json.dumps(item, ensure_ascii=False) + "\n")
                accepted += 1
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                bad.write(json.dumps({"line": line_no, "reasons": ["invalid_json"], "error": str(exc)}) + "\n")
                rejected += 1

    manifest = {"cleaner_version": "2.0.0", "accepted": accepted, "rejected": rejected, "duplicates": duplicates, "min_score": args.min_score, "output": str(args.output), "quarantine": str(args.quarantine)}
    args.output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

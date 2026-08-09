"""Streaming, format-aware dataset processor for Phase 36.

The processor is intentionally conservative: unsupported formats are skipped rather
than guessed, and every accepted record keeps source/license metadata. It is designed
for Colab/GPU or a CPU worker and does not load an entire corpus into memory.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterator

try:
    import pyarrow.parquet as pq
except ImportError:
    pq = None

SECRET_RE = re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]|AKIA[0-9A-Z]{16}|-----BEGIN .*?PRIVATE KEY-----")
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_RE = re.compile(r"\b(?:\+?\d[\d ()-]{8,}\d)\b")
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    text = html.unescape(text)
    text = TAG_RE.sub(" ", text)
    return WS_RE.sub(" ", text).strip()


def security_flags(text: str) -> tuple[bool, bool]:
    return bool(EMAIL_RE.search(text) or PHONE_RE.search(text)), bool(SECRET_RE.search(text))


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()


def rows(path: Path) -> Iterator[dict]:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".html", ".htm"}:
        yield {"text": path.read_text(encoding="utf-8", errors="ignore"), "source": str(path)}
    elif suffix == ".jsonl":
        with path.open(encoding="utf-8", errors="ignore") as f:
            for line in f:
                try:
                    value = json.loads(line)
                    yield {"text": value.get("text", ""), "source": str(path), **({"license": value["license"]} if "license" in value else {})}
                except json.JSONDecodeError:
                    continue
    elif suffix == ".json":
        try:
            value = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            values = value if isinstance(value, list) else [value]
            for item in values:
                if isinstance(item, dict):
                    yield {"text": item.get("text", ""), "source": str(path), **({"license": item["license"]} if "license" in item else {})}
        except json.JSONDecodeError:
            return
    elif suffix == ".csv":
        with path.open(newline="", encoding="utf-8", errors="ignore") as f:
            for item in csv.DictReader(f):
                text = item.get("text") or item.get("content") or ""
                yield {"text": text, "source": str(path), "license": item.get("license", "")}
    elif suffix == ".parquet" and pq is not None:
        table = pq.ParquetFile(path)
        for batch in table.iter_batches(batch_size=2048):
            for item in batch.to_pylist():
                if isinstance(item, dict):
                    yield {"text": item.get("text") or item.get("content") or "", "source": str(path), "license": item.get("license", "")}


def process(input_dir: Path, output: Path, min_chars: int) -> Counter:
    stats = Counter()
    seen: set[str] = set()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as out:
        for path in input_dir.rglob("*"):
            if not path.is_file():
                continue
            for row in rows(path):
                stats["records_seen"] += 1
                text = normalize(str(row.get("text", "")))
                if len(text) < min_chars:
                    stats["too_short"] += 1
                    continue
                pii, secret = security_flags(text)
                if pii:
                    stats["pii_rejected"] += 1
                    continue
                if secret:
                    stats["secret_rejected"] += 1
                    continue
                key = digest(text)
                if key in seen:
                    stats["duplicate"] += 1
                    continue
                seen.add(key)
                out.write(json.dumps({"text": text, "sha256": key, "source": row.get("source"), "license": row.get("license", "")}, ensure_ascii=False) + "\n")
                stats["accepted"] += 1
    return stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw")
    parser.add_argument("--output", default="data/processed/cleaned.jsonl")
    parser.add_argument("--min-chars", type=int, default=80)
    args = parser.parse_args()
    stats = process(Path(args.input), Path(args.output), args.min_chars)
    print(json.dumps(dict(stats), indent=2))


if __name__ == "__main__":
    main()

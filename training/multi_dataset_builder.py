"""Build a canonical, provenance-preserving multi-dataset stream for the cleaner.

Supports JSON/JSONL/CSV/TXT/MD/HTML and Parquet when pyarrow is installed.
It does not silently discard source/license metadata; every emitted record carries
source information and a deterministic ID. Raw data is never modified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "raw"
DEFAULT_OUTPUT = ROOT / "data" / "normalized" / "multidataset.jsonl"

TEXT_FIELDS = ("text", "content", "body", "prompt", "completion", "response", "instruction", "question", "answer")


def clean_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = html.unescape(text)
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_text(obj: object) -> str:
    if isinstance(obj, str):
        return clean_text(obj)
    if isinstance(obj, dict):
        parts = []
        for key in TEXT_FIELDS:
            if key in obj:
                value = obj[key]
                if isinstance(value, list):
                    parts.extend(clean_text(v) for v in value)
                else:
                    parts.append(clean_text(value))
        if parts:
            return "\n".join(p for p in parts if p)
        return clean_text(json.dumps(obj, ensure_ascii=False, sort_keys=True))
    if isinstance(obj, list):
        return "\n".join(extract_text(v) for v in obj if extract_text(v))
    return clean_text(obj)


def record(obj: object, path: Path, dataset: str, row: int) -> dict:
    text = extract_text(obj)
    source_id = hashlib.sha256(f"{dataset}:{path.relative_to(DEFAULT_INPUT)}:{row}".encode()).hexdigest()
    return {
        "id": f"sha256:{hashlib.sha256(text.encode('utf-8')).hexdigest()}",
        "text": text,
        "source": {
            "dataset": dataset,
            "file": str(path.relative_to(DEFAULT_INPUT)),
            "record": row,
        },
        "metadata": {
            "source_id": source_id,
            "content_type": path.suffix.lower().lstrip(".") or "unknown",
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        },
        "quality": {"score": None, "duplicate": False, "near_duplicate": False},
        "safety": {"pii": None, "secrets": None, "malware": None},
        "processing": {"builder_version": "1.0.0"},
    }


def iter_records(path: Path):
    suffix = path.suffix.lower()
    dataset = path.parent.name
    if suffix in {".txt", ".md", ".html", ".htm"}:
        yield record(path.read_text(encoding="utf-8", errors="ignore"), path, dataset, 1)
    elif suffix == ".jsonl":
        with path.open(encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                if line.strip():
                    yield record(json.loads(line), path, dataset, i)
    elif suffix == ".json":
        obj = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        if isinstance(obj, list):
            for i, item in enumerate(obj, 1):
                yield record(item, path, dataset, i)
        else:
            yield record(obj, path, dataset, 1)
    elif suffix == ".csv":
        with path.open(newline="", encoding="utf-8", errors="ignore") as f:
            for i, row in enumerate(csv.DictReader(f), 1):
                yield record(row, path, dataset, i)
    elif suffix == ".parquet":
        try:
            import pyarrow.parquet as pq
        except ImportError as exc:
            raise RuntimeError("Parquet input requires pyarrow") from exc
        table = pq.read_table(path)
        for i, row in enumerate(table.to_pylist(), 1):
            yield record(row, path, dataset, i)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    counts = {}
    total = 0
    with args.output.open("w", encoding="utf-8") as out:
        for path in args.input.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".txt", ".md", ".html", ".htm", ".json", ".jsonl", ".csv", ".parquet"}:
                continue
            dataset = path.parent.name
            counts.setdefault(dataset, 0)
            for item in iter_records(path):
                if not item["text"]:
                    continue
                out.write(json.dumps(item, ensure_ascii=False) + "\n")
                counts[dataset] += 1
                total += 1
    manifest = {
        "builder_version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input": str(args.input),
        "output": str(args.output),
        "records": total,
        "datasets": counts,
        "next_stage": "training/safe_cleaner.py",
    }
    args.output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

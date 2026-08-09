from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
STATE = ROOT / "data" / "pipeline_state.json"


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"runs": []}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_local_files() -> dict:
    # Deterministic safety gate for artifacts that already exist locally.
    files = [p for p in RAW.rglob("*") if p.is_file()]
    manifest = [{"path": str(p.relative_to(RAW)), "sha256": sha256_file(p), "bytes": p.stat().st_size} for p in files]
    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "artifact_manifest.json").write_text(json.dumps(manifest, indent=2))
    return {"files": len(files), "bytes": sum(x["bytes"] for x in manifest)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproducible TechSpace dataset acquisition/cleaning/training orchestrator")
    parser.add_argument("--stage", choices=["acquire", "clean", "train", "evaluate", "promote", "all"], default="all")
    parser.add_argument("--dataset", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    record = {"run_id": run_id, "stage": args.stage, "datasets": args.dataset, "status": "started"}

    if args.dry_run:
        print(json.dumps(record, indent=2))
        return

    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    if args.stage in {"clean", "all"}:
        # Cleaning workers are intentionally externalized: no destructive in-place mutation.
        # They consume raw data and write versioned processed shards.
        stats = scan_local_files()
        record["artifact_scan"] = stats

    if args.stage in {"acquire", "all"}:
        print("Acquire stage: invoke the configured HF/Hub downloader before cleaning.")
    if args.stage in {"train", "all"}:
        print("Train stage: invoke the configured Colab/GPU trainer after validation.")
    if args.stage in {"evaluate", "all"}:
        print("Evaluate stage: require benchmark and safety gates before promotion.")
    if args.stage in {"promote", "all"}:
        print("Promote stage: only immutable, evaluated artifacts may enter production.")

    record["status"] = "completed"
    s = state()
    s["runs"].append(record)
    STATE.write_text(json.dumps(s, indent=2))
    print(json.dumps(record, indent=2))

if __name__ == "__main__":
    main()

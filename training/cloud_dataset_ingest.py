"""Stream Hugging Face datasets into sharded JSONL without filling local storage.

Environment:
  HF_TOKEN          optional for gated/private datasets
  GCS_BUCKET        optional gs:// bucket for immediate shard uploads

Example:
  python training/cloud_dataset_ingest.py --dataset fineweb2 --max-records 100000

The script intentionally keeps a small local cache and uploads completed shards
before continuing. It does not put credentials in source control.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

import yaml
from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "training" / "datasets.yaml"


def load_registry() -> dict:
    with REGISTRY.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def upload(path: Path, destination: str | None) -> None:
    if not destination:
        return
    subprocess.run(["gcloud", "storage", "cp", str(path), destination.rstrip("/") + "/" + path.name], check=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--split", default="train")
    p.add_argument("--max-records", type=int, default=100_000)
    p.add_argument("--shard-size", type=int, default=5_000)
    p.add_argument("--output", type=Path, default=ROOT / "data" / "cache")
    p.add_argument("--revision", default=None)
    args = p.parse_args()

    registry = load_registry()
    entry = next((x for x in registry["datasets"] if x["id"] == args.dataset and x.get("enabled", True)), None)
    if not entry:
        raise SystemExit(f"Unknown or disabled dataset: {args.dataset}")

    args.output.mkdir(parents=True, exist_ok=True)
    kwargs = {"path": entry["source"], "split": args.split, "streaming": True}
    if args.revision:
        kwargs["revision"] = args.revision
    token = os.getenv("HF_TOKEN")
    if token:
        kwargs["token"] = token

    ds = load_dataset(**kwargs)
    bucket = os.getenv("GCS_BUCKET")
    written = 0
    shard = 0
    while written < args.max_records:
        count = 0
        path = args.output / f"{args.dataset}-{shard:05d}.jsonl"
        with path.open("w", encoding="utf-8") as out:
            for item in ds:
                out.write(json.dumps(item, ensure_ascii=False, default=str) + "\n")
                written += 1
                count += 1
                if count >= args.shard_size or written >= args.max_records:
                    break
        if count == 0:
            path.unlink(missing_ok=True)
            break
        upload(path, bucket)
        if bucket:
            path.unlink(missing_ok=True)
        shard += 1
        if count < args.shard_size:
            break

    print(json.dumps({"dataset": args.dataset, "records": written, "shards": shard, "gcs": bucket}, indent=2))


if __name__ == "__main__":
    main()

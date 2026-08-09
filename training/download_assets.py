from __future__ import annotations

import argparse
from pathlib import Path
from huggingface_hub import snapshot_download
import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "training" / "assets.yaml"


def load():
    return yaml.safe_load(MANIFEST.read_text())


def download(kind: str, name: str | None, revision_override: str | None = None):
    cfg = load()
    items = cfg[kind]
    if name:
        items = [x for x in items if x["id"] == name]
        if not items:
            raise SystemExit(f"Unknown {kind[:-1]} asset: {name}")
    base = ROOT / "data" / "raw" / kind
    for item in items:
        revision = revision_override or item.get("revision") or "main"
        target = base / item["id"]
        target.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {item['repo']} -> {target} (revision={revision})")
        snapshot_download(
            repo_id=item["repo"],
            repo_type="model" if kind == "models" else "dataset",
            revision=revision,
            local_dir=str(target),
            local_dir_use_symlinks=False,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download approved TechSpace AI assets from Hugging Face")
    parser.add_argument("kind", choices=["models", "datasets"])
    parser.add_argument("--name")
    parser.add_argument("--revision", help="Only for reproducible test downloads; production must pin an immutable revision")
    args = parser.parse_args()
    download(args.kind, args.name, args.revision)

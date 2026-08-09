from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download

MODELS = {
    "qwen3-30b-a3b": "Qwen/Qwen3-30B-A3B",
    "qwen3-235b-a22b": "Qwen/Qwen3-235B-A22B",
    "qwen3-coder-30b-a3b-instruct": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
    "phi-4": "microsoft/phi-4",
    "smollm3-3b": "HuggingFaceTB/SmolLM3-3B",
    "qwen3-embedding-8b": "Qwen/Qwen3-Embedding-8B",
    "qwen3-embedding-4b": "Qwen/Qwen3-Embedding-4B",
    "bge-m3": "BAAI/bge-m3",
    "bge-reranker-v2-m3": "BAAI/bge-reranker-v2-m3",
}

DATASETS = {
    "fineweb2": "HuggingFaceFW/fineweb-2",
    "dolma-v1_7": "allenai/dolma",
    "open-web-math": "open-web-math/open-web-math",
    "aya-collection": "CohereLabs/aya_collection",
    "the-stack-v2": "bigcode/the-stack-v2",
}


def download(repo: str, destination: Path, revision: str | None = None) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=repo, repo_type="dataset" if repo in DATASETS.values() else "model", revision=revision, local_dir=str(destination), local_dir_use_symlinks=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download approved TechSpace AI HF assets")
    parser.add_argument("--kind", choices=["models", "datasets"], required=True)
    parser.add_argument("--name", help="specific manifest name; omit to download all")
    parser.add_argument("--out", default="data/raw")
    args = parser.parse_args()
    catalog = MODELS if args.kind == "models" else DATASETS
    items = {args.name: catalog[args.name]} if args.name else catalog
    for name, repo in items.items():
        print(f"Downloading {name}: {repo}")
        download(repo, Path(args.out) / args.kind / name)

if __name__ == "__main__":
    main()

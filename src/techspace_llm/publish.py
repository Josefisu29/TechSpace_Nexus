from __future__ import annotations

import argparse
import os
from huggingface_hub import HfApi


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--type", choices=["model", "dataset"], default="model")
    parser.add_argument("--private", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is required and must be supplied through the environment.")

    api = HfApi(token=token)
    api.create_repo(args.repo, repo_type=args.type, private=args.private, exist_ok=True)
    api.upload_folder(
        folder_path=args.folder,
        repo_id=args.repo,
        repo_type=args.type,
        commit_message="publish: upload TechSpace artifact",
    )
    print(f"Published {args.folder} to {args.repo}")


if __name__ == "__main__":
    main()

"""
Upload inconvenience-msds dataset to HuggingFace Hub.

Prerequisites:
    pip install -U huggingface_hub
    export HF_TOKEN=hf_xxxxxxxxxxxx     # or `huggingface-cli login`
    Repo must exist: https://huggingface.co/datasets/Yuyongkim/inconvenience-msds

Usage:
    python scripts/push_to_hf.py
    python scripts/push_to_hf.py --dry-run
"""

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "data" / "hf_dataset"
REPO_ID = "Yuyongkim/inconvenience-msds"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--repo-id", default=REPO_ID)
    args = parser.parse_args()

    train_path = DATASET_DIR / "train.jsonl"
    readme_path = DATASET_DIR / "README.md"

    for p in (train_path, readme_path):
        if not p.exists():
            print(f"Missing: {p}", file=sys.stderr)
            sys.exit(1)

    size_mb = train_path.stat().st_size / 1024 / 1024
    print(f"Repo:   {args.repo_id}")
    print(f"Folder: {DATASET_DIR}")
    print(f"  - train.jsonl  ({size_mb:.1f} MB)")
    print(f"  - README.md    ({readme_path.stat().st_size} B)")

    if args.dry_run:
        print("\n[dry-run] not uploading.")
        return

    token = os.environ.get("HF_TOKEN")
    if not token:
        print("\nNote: HF_TOKEN not in env; relying on `huggingface-cli login` cache.")

    from huggingface_hub import HfApi
    api = HfApi(token=token)

    print("\nUploading folder...")
    api.upload_folder(
        folder_path=str(DATASET_DIR),
        repo_id=args.repo_id,
        repo_type="dataset",
        commit_message="Initial release: 48,966 chemicals × MSDS sections in Korean braille",
    )
    print(f"\nDone: https://huggingface.co/datasets/{args.repo_id}")


if __name__ == "__main__":
    main()

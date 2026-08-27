"""Publish the three public-safety braille catalogues to HuggingFace.

Separate from `push_to_hf.py` on purpose. That one ships a single file for a
single catalogue; this one ships one file per domain plus a card whose config
block names them, because the whole point of the paper is that the three are
not interchangeable and a reader who wants the pesticide rows should not have
to filter a merged file.

The token is read through `scripts/keys.py` rather than the environment, which
is where every other fetcher in this repository now reads its credentials.

Usage:
    python scripts/push_paper2_to_hf.py --dry-run
    python scripts/push_paper2_to_hf.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import keys  # noqa: E402

DATASET_DIR = PROJECT_ROOT / "data" / "paper2_dataset"
REPO_ID = "Yuyongkim/inconvenience-public-safety"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--repo-id", default=REPO_ID)
    ap.add_argument("--private", action="store_true",
                    help="create the repo private; the companion dataset is public")
    args = ap.parse_args()

    manifest_path = DATASET_DIR / "manifest.json"
    readme_path = DATASET_DIR / "README.md"
    if not manifest_path.exists() or not readme_path.exists():
        raise SystemExit("run scripts/export_paper2_dataset.py first")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    domains = manifest.get("domains", {})

    print(f"repo: {args.repo_id}")
    total = 0
    for key in domains:
        path = DATASET_DIR / f"{key}.jsonl"
        if not path.exists():
            raise SystemExit(f"manifest names {key} but {path.name} is missing")
        mb = path.stat().st_size / 1024 / 1024
        total += mb
        print(f"  {path.name:18s} {mb:>7.1f} MB  "
              f"{domains[key]['records']:>6,} records")
    print(f"  {'README.md':18s} {readme_path.stat().st_size / 1024:>7.1f} KB")
    print(f"  {'manifest.json':18s} {manifest_path.stat().st_size / 1024:>7.1f} KB")
    print(f"  total {total:.1f} MB, "
          f"{manifest['totals']['records']:,} records, "
          f"{manifest['totals']['braille_cells']:,} braille cells")

    if args.dry_run:
        print("\n[dry-run] nothing uploaded.")
        return

    from huggingface_hub import HfApi
    api = HfApi(token=keys.get("hf_token"))

    api.create_repo(repo_id=args.repo_id, repo_type="dataset",
                    private=args.private, exist_ok=True)
    print(f"\nrepo ready ({'private' if args.private else 'public'})")

    api.upload_folder(
        folder_path=str(DATASET_DIR),
        repo_id=args.repo_id,
        repo_type="dataset",
        commit_message=(
            "Three Korean public-safety registers in braille: "
            f"{manifest['totals']['records']:,} records across "
            f"{len(domains)} domains"),
    )
    print(f"-> https://huggingface.co/datasets/{args.repo_id}")


if __name__ == "__main__":
    main()

"""Do public fingerspelling datasets carry the field a person-independent split needs?

`fingerspelling_eval.py` refuses to report a random split. That is only useful
if the data supports the alternative, so this checks whether the public
fingerspelling datasets actually record who signed each sample.

The answer decides how much of the literature could have used a signer-grouped
split. If the field is missing, person-independent evaluation on those datasets
is not merely undone; it is impossible, and every published accuracy on them
carries the inflation measured in `track-c-eval-results.json`.

Queries the Hugging Face datasets API, which is public and needs no token.

Usage:
    python scripts/dataset_signer_audit.py
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = PROJECT_ROOT / "docs" / "track-c-dataset-audit.json"

# The fingerspelling / sign-alphabet datasets a practitioner would actually
# reach for, by download count on the Hub.
DATASETS = [
    "Voxel51/American-Sign-Language-MNIST",
    "Marxulia/asl_sign_languages_alphabets_v03",
    "shpouladi/American-Sign-Language-Dataset",
    "just-me7ss/American-Sign-Language-Dataset",
    "akasheroor/American-Sign-Language-Dataset",
    "ZahidYasinMittha/American-Sign-Language-Dataset",
    "Namonpas/thai-sign-language-tsl51",
    "PishangShedappp/malaysian-sign-language-dataset-v1",
    "silentone0725/Indian_Sign_Language_Data.gov_Rencoded",
]

# Any of these in a column name would let folds be grouped by person.
SIGNER_KEYS = {
    "signer", "signer_id", "subject", "subject_id", "person", "person_id",
    "participant", "participant_id", "user", "user_id", "speaker", "actor",
}


def fetch(url: str) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "signer-audit/1.0"})
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
        return None


def columns_of(repo: str) -> list[str]:
    """Column names, from the datasets-server if it has parsed the repo."""
    info = fetch(f"https://datasets-server.huggingface.co/info?dataset={urllib.parse.quote(repo)}")
    names: list[str] = []
    if info:
        for cfg in (info.get("dataset_info") or {}).values():
            for split in (cfg.get("features") or {}):
                names.append(split)
    if names:
        return sorted(set(names))

    # Fall back to the card metadata, which lists features for most datasets.
    card = fetch(f"https://huggingface.co/api/datasets/{repo}")
    if not card:
        return []
    for entry in (card.get("cardData") or {}).get("dataset_info") or []:
        if isinstance(entry, dict):
            for feat in entry.get("features") or []:
                if isinstance(feat, dict) and "name" in feat:
                    names.append(feat["name"])
    di = (card.get("cardData") or {}).get("dataset_info")
    if isinstance(di, dict):
        for feat in di.get("features") or []:
            if isinstance(feat, dict) and "name" in feat:
                names.append(feat["name"])
    return sorted(set(names))


def main() -> None:
    rows = []
    print(f"{'dataset':52s} {'columns':38s} signer?")
    print("-" * 104)
    for repo in DATASETS:
        cols = columns_of(repo)
        has = sorted({c for c in cols if c.lower() in SIGNER_KEYS})
        rows.append({"dataset": repo, "columns": cols, "signer_fields": has,
                     "supports_person_independent": bool(has)})
        shown = ", ".join(cols[:4]) if cols else "(not resolved)"
        print(f"{repo[:52]:52s} {shown[:38]:38s} {'YES' if has else 'no'}")

    resolved = [r for r in rows if r["columns"]]
    supported = [r for r in resolved if r["supports_person_independent"]]
    print()
    print(f"resolved {len(resolved)}/{len(rows)} datasets; "
          f"{len(supported)} carry a signer field")
    if not supported:
        print("\nNone of them can be split by signer. On these datasets a "
              "person-independent\nevaluation is not undone, it is impossible.")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({
        "source": "Hugging Face datasets-server / dataset cards",
        "signer_key_candidates": sorted(SIGNER_KEYS),
        "datasets": rows,
        "resolved": len(resolved),
        "with_signer_field": len(supported),
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n-> {OUT_JSON}")


if __name__ == "__main__":
    main()

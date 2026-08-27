"""Export the three paper-2 catalogues as one dataset, split by domain.

Paper 1 shipped one catalogue and so one file. Three catalogues could be
concatenated the same way, but that would throw away the thing the paper is
about: the domains differ, and a reader who wants the pesticide rows should not
have to filter a merged file to find them. So this writes one JSONL per domain
plus a manifest, which is the shape HuggingFace configs expect.

Each record carries the adapted Korean text, the braille, and the sections in
reading order. The sections are kept separately from the flat text because the
reading order is the adapter's contribution and collapsing it into one string
would make it unrecoverable.

The source records are not included. All three registers are public APIs, the
fetchers name the endpoints, and redistributing government text this project
merely passed through is neither necessary nor ours to do.

Usage:
    python scripts/export_paper2_dataset.py [--limit 100]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.adapters.drug import DrugAdapter  # noqa: E402
from pipeline.adapters.incident import IncidentAdapter  # noqa: E402
from pipeline.adapters.pesticide import PesticideAdapter  # noqa: E402
from pipeline.ko_braille import encode_korean_braille  # noqa: E402

CORPORA = PROJECT_ROOT / "data" / "paper2"
OUT = PROJECT_ROOT / "data" / "paper2_dataset"

DOMAINS = [
    ("drug", DrugAdapter, "의약품 허가정보 및 복약정보 (식품의약품안전처)"),
    ("pesticide", PesticideAdapter, "농약 등록정보 (식품의약품안전처, 식품안전나라)"),
    ("incident", IncidentAdapter, "국내재해사례 (한국산업안전보건공단)"),
]


def export(key: str, adapter_cls, limit: int | None) -> dict:
    path = CORPORA / f"{key}_corpus.json"
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    records = adapter_cls().adapt_many(raw.get("records", []))
    if limit:
        records = records[:limit]

    OUT.mkdir(parents=True, exist_ok=True)
    chars = cells = 0
    with (OUT / f"{key}.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for rec in records:
            text = rec.text()
            braille = encode_korean_braille(text)
            chars += len(text)
            cells += len(braille)
            f.write(json.dumps({
                "domain": rec.domain,
                "record_id": rec.record_id,
                "name": rec.name,
                "sections": [{"title": s.title, "text": s.text,
                              "braille": encode_korean_braille(s.as_text())}
                             for s in rec.sections],
                "text": text,
                "braille": braille,
                "text_chars": len(text),
                "braille_cells": len(braille),
                "meta": rec.meta,
            }, ensure_ascii=False) + "\n")

    return {
        "records": len(records),
        "text_chars": chars,
        "braille_cells": cells,
        "expansion_ratio": round(cells / chars, 3) if chars else 0.0,
        "source": raw.get("source", ""),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    manifest = {}
    for key, cls, label in DOMAINS:
        stats = export(key, cls, args.limit or None)
        if not stats:
            print(f"{key}: no corpus, skipped")
            continue
        stats["label"] = label
        manifest[key] = stats
        print(f"{key:10s} {stats['records']:>7,} records  "
              f"{stats['text_chars']:>10,} chars  "
              f"{stats['braille_cells']:>11,} cells  "
              f"ratio {stats['expansion_ratio']:.2f}")

    if not manifest:
        raise SystemExit("nothing to export; run the fetchers first")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "manifest.json").write_text(
        json.dumps({
            "name": "kosha-braille-public-safety",
            "rules": "2017 한국 점자 규정 (문화체육관광부 고시 제2017-15호)",
            "note": "Source records are not redistributed; all three registers "
                    "are public APIs and the fetchers name the endpoints.",
            "domains": manifest,
            "totals": {
                "records": sum(d["records"] for d in manifest.values()),
                "text_chars": sum(d["text_chars"] for d in manifest.values()),
                "braille_cells": sum(d["braille_cells"] for d in manifest.values()),
            },
        }, ensure_ascii=False, indent=1), encoding="utf-8")

    total = sum(d["records"] for d in manifest.values())
    print(f"\n{total:,} records across {len(manifest)} domains")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()

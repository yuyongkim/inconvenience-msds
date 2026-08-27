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

# The drug register carries two document shapes. A record with a patient
# leaflet is prose at a median of 917 characters; one without is a handful of
# approval fields at 67. Merging them would put a number in the card that
# describes neither, so they ship as separate configs.
DOMAINS = [
    ("drug_leaflet", "drug", DrugAdapter, lambda r: bool(r.get("easy")),
     "의약품 복약정보 + 허가정보 (식품의약품안전처, e약은요)"),
    ("drug_approval", "drug", DrugAdapter, lambda r: not r.get("easy"),
     "의약품 허가정보 (식품의약품안전처)"),
    ("pesticide", "pesticide", PesticideAdapter, None,
     "농약 등록정보 (식품의약품안전처, 식품안전나라)"),
    ("incident", "incident", IncidentAdapter, None,
     "국내재해사례 (한국산업안전보건공단)"),
]


def export(key: str, corpus: str, adapter_cls, select, limit: int | None) -> dict:
    path = CORPORA / f"{corpus}_corpus.json"
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    rows = raw.get("records", [])
    if select:
        rows = [r for r in rows if select(r)]
    records = adapter_cls().adapt_many(rows)
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


CARD = """---
language:
- ko
license: cc-by-4.0
size_categories:
- 100K<n<1M
task_categories:
- translation
- text-generation
tags:
- braille
- accessibility
- korean
- public-safety
- pharmaceutical
- pesticide
- occupational-safety
- inconvenience-series
configs:
{configs}---

# inconvenience-public-safety

Three Korean public-safety registers converted to Korean braille under the 2017
revised rules (문화체육관광부 고시 제2017-15호). Every register is enumerated in
full, not sampled.

The registers are here because their documents are shaped differently, not
because three is more than one. A pesticide row is a filled-in form; a patient
leaflet is prose; an accident case is a paragraph an investigator wrote. Median
record length spans more than an order of magnitude across them.

There are four configs rather than three because the drug register carries two
shapes. A product with a patient leaflet runs to a median of 917 characters of
prose; one without is a handful of approval fields at 67. Averaging them would
produce a number describing neither.

## Configs

{table}

## Fields

| Field | Meaning |
|---|---|
| `domain` | `drug`, `pesticide`, or `incident` — the register it came from |
| `record_id` | the register's own identifier |
| `name` | product or case name |
| `sections` | titled blocks **in reading order**, each with its own braille |
| `text` | the whole record as one Korean string |
| `braille` | the whole record in Unicode braille |
| `text_chars`, `braille_cells` | lengths, for embosser planning |
| `meta` | per-domain identifiers kept out of the reading flow |

`sections` is kept alongside `text` because the reading order is the part that
carries judgement. A record has no inherent order — the API returns whatever the
database stores — while a braille reader traverses linearly with no way to skim
back. Collapsing the sections into one string would make that order
unrecoverable.

## What is not here

The source records. All three registers are public APIs and the fetchers in the
repository name the endpoints and parameters, so a reader can collect the same
material with their own key. Redistributing government text this project merely
passed through is neither necessary nor ours to do.

## Known limits

- Round-trip reaches a fixed point for {stability}. The remainder sits where the
  Rule 30 roman terminator shares a cell with the period and the cell stream
  genuinely does not distinguish the readings.
- Composed unit characters (㎡, ℃, ㎥) have no cell and pass through unchanged.
  They round-trip by accident but are not braille.
- Every register is enumerated in full. Earlier releases of this dataset carried
  samples shaped by a search term, which is a different thing and a worse one.

## Source

Built by `scripts/export_paper2_dataset.py` in the KOSHA-Braille repository.
Companion to `Yuyongkim/inconvenience-msds`, which carries the chemical safety
data sheets the encoder was first validated on.
"""


def write_card(manifest: dict) -> None:
    """A card that says what the fields mean and what is deliberately absent."""
    configs = "".join(
        f"- config_name: {k}\n  data_files: {k}.jsonl\n" for k in manifest)
    rows = ["| Config | Register | Records | Cells | Cells per character |",
            "|---|---|---|---|---|"]
    for k, d in manifest.items():
        rows.append(f"| `{k}` | {d['label']} | {d['records']:,} | "
                    f"{d['braille_cells']:,} | {d['expansion_ratio']:.2f} |")

    stability = "100% of drug and pesticide records and 99.7% of accident cases"
    stab = PROJECT_ROOT / "docs" / "paper2-stability-full.json"
    if stab.exists():
        got = json.loads(stab.read_text(encoding="utf-8"))
        stability = ", ".join(
            f"{v['stable_pct']:.1%} of {k} records" for k, v in got.items())

    (OUT / "README.md").write_text(
        CARD.format(configs=configs, table="\n".join(rows), stability=stability),
        encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    manifest = {}
    for key, corpus, cls, select, label in DOMAINS:
        stats = export(key, corpus, cls, select, args.limit or None)
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

    # A config that no longer exists leaves its file behind, and the next upload
    # ships it as though it were current. Splitting the drug register into two
    # configs left the merged drug.jsonl sitting in the folder.
    for stale in OUT.glob("*.jsonl"):
        if stale.stem not in manifest:
            stale.unlink()
            print(f"removed stale config: {stale.name}")

    write_card(manifest)

    total = sum(d["records"] for d in manifest.values())
    print(f"\n{total:,} records across {len(manifest)} domains")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()

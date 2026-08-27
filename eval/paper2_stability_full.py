"""Fixed-point stability over every record, not an 800-record sample.

`eval/paper2_validation.py` samples, because exact and near round-trip are
reported alongside rule checking and the whole thing has to stay quick enough to
run while editing. Stability is the number the paper actually rests on, and a
sample is a weaker claim than the corpus, so it is measured separately over all
of it.

The distinction matters for the incident domain in particular. Its failures are
rare and concentrated where roman and Korean interlock, which is exactly the
kind of distribution a sample can miss entirely or over-weight by a factor of
two.

Usage:
    python eval/paper2_stability_full.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.adapters.drug import DrugAdapter  # noqa: E402
from pipeline.adapters.incident import IncidentAdapter  # noqa: E402
from pipeline.adapters.pesticide import PesticideAdapter  # noqa: E402
from pipeline.ko_braille import encode_korean_braille  # noqa: E402
from pipeline.ko_braille_decoder import decode_korean_braille  # noqa: E402

CORPORA = PROJECT_ROOT / "data" / "paper2"
OUT = PROJECT_ROOT / "docs" / "paper2-stability-full.json"

DOMAINS = [("drug", DrugAdapter), ("pesticide", PesticideAdapter),
           ("incident", IncidentAdapter)]


def stable(text: str) -> bool:
    """Encode, decode, encode, decode: did the second pass change anything?"""
    try:
        once = decode_korean_braille(encode_korean_braille(text))
        return bool(once) and decode_korean_braille(encode_korean_braille(once)) == once
    except Exception:
        return False


def main() -> None:
    results = {}
    for key, cls in DOMAINS:
        path = CORPORA / f"{key}_corpus.json"
        if not path.exists():
            print(f"{key}: no corpus, skipped")
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        records = cls().adapt_many(raw.get("records", []))
        bad = [r.record_id for r in records if not stable(r.text())]
        n = len(records) or 1
        results[key] = {
            "records": len(records),
            "unstable": len(bad),
            "stable_pct": round((len(records) - len(bad)) / n, 5),
            # Enough to find them again without turning the file into a corpus.
            "unstable_ids": bad[:40],
        }
        print(f"{key:10s} {len(records) - len(bad):>6,}/{len(records):,} stable "
              f"= {results[key]['stable_pct']:.3%}  ({len(bad)} unstable)",
              flush=True)

    if not results:
        raise SystemExit("no corpora; run the fetchers first")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()

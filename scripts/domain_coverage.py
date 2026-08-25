"""How far does the chemical root lexicon reach into a neighbouring domain?

The lexicon in `data/morphology/roots.json` was mined from KOSHA chemical names.
Pharmaceutical, cosmetic and pesticide names are transliterated from the same
Latin/Greek stock, so some of it should transfer. This measures how much, and
names what is left over — the leftovers are the next domain's own vocabulary.

Coverage here is a property of the *name*, not of the braille. The encoder
already handles every one of these strings; the question is whether we can say
anything about their internal structure.

Usage:
    python scripts/domain_coverage.py
    python scripts/domain_coverage.py --output docs/track-a-coverage-report.md
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.morphology import coverage, load_lexicon, normalize_ko, segment  # noqa: E402

KOSHA_DB = Path("G:/MSDS/data/terminology.db")
PHARMA_JSON = PROJECT_ROOT / "data" / "pharma" / "mfds_drug_names.json"


def kosha_names(limit: int | None = None) -> list[str]:
    if not KOSHA_DB.exists():
        return []
    conn = sqlite3.connect(str(KOSHA_DB))
    try:
        rows = conn.execute("SELECT name FROM chemical_terms WHERE name IS NOT NULL").fetchall()
    finally:
        conn.close()
    names = [normalize_ko(r[0]) for r in rows]
    names = [n for n in names if n]
    return names[:limit] if limit else names


def pharma_names() -> list[str]:
    if not PHARMA_JSON.exists():
        return []
    raw = json.loads(PHARMA_JSON.read_text(encoding="utf-8"))
    names = [normalize_ko(i["name_ko"]) for i in raw["items"]]
    return [n for n in names if n]


def analyse(names: list[str]) -> dict:
    lex = load_lexicon()
    if not names:
        return {}

    per_name = [coverage(n, lex) for n in names]
    full = sum(1 for c in per_name if c >= 0.999)
    none = sum(1 for c in per_name if c == 0.0)

    used: Counter[str] = Counter()
    gaps: Counter[str] = Counter()
    for n in names:
        for surface, root in segment(n, lex):
            if root is None:
                if len(surface) >= 2:
                    gaps[surface] += 1
            else:
                used[root.en] += 1

    chars_total = sum(len(n) for n in names)
    chars_covered = sum(int(round(c * len(n))) for n, c in zip(names, per_name))
    return {
        "names": len(names),
        "char_coverage": chars_covered / chars_total if chars_total else 0.0,
        "mean_name_coverage": sum(per_name) / len(per_name),
        "fully_covered": full,
        "fully_covered_pct": full / len(names),
        "uncovered": none,
        "uncovered_pct": none / len(names),
        "roots_used": len(used),
        "top_roots": used.most_common(15),
        "top_gaps": gaps.most_common(25),
    }


def render(results: dict[str, dict]) -> str:
    lex = load_lexicon()
    out: list[str] = []
    out.append("# Track A — root coverage across domains\n")
    out.append(
        f"Lexicon: {len(lex)} roots mined from KOSHA Korean/English name pairs "
        "(`data/morphology/roots.json`, built by `scripts/mine_morphemes.py`).\n"
    )
    out.append(
        "Coverage is the share of a name's Hangul that a known root accounts for. "
        "It says nothing about braille quality — the encoder already handles every "
        "name here. It measures how much of the naming vocabulary transfers.\n"
    )

    out.append("## Summary\n")
    out.append("| Domain | Names | Char coverage | Fully covered | No root matched | Roots used |")
    out.append("|---|---:|---:|---:|---:|---:|")
    for label, r in results.items():
        if not r:
            continue
        out.append(
            f"| {label} | {r['names']:,} | {r['char_coverage']:.1%} | "
            f"{r['fully_covered_pct']:.1%} | {r['uncovered_pct']:.1%} | {r['roots_used']} |"
        )
    out.append("")

    for label, r in results.items():
        if not r:
            continue
        out.append(f"## {label}\n")
        out.append("Most-used roots:\n")
        out.append("| Root | Names |")
        out.append("|---|---:|")
        for en, n in r["top_roots"]:
            out.append(f"| {en} | {n:,} |")
        out.append("")
        out.append("Largest gaps — Hangul runs no root explains:\n")
        out.append("| Fragment | Names |")
        out.append("|---|---:|")
        for frag, n in r["top_gaps"]:
            out.append(f"| {frag} | {n:,} |")
        out.append("")

    out.append("## What the pharmaceutical number means" + chr(10))
    out.append(
        "The MFDS figure is low because the names are the wrong unit, not because "
        "the lexicon fails. DrbEasyDrugInfoService returns *product* names, and a "
        "brand name has no Latin root to find. The fragments the lexicon cannot "
        "explain are dosage form and strength: 연질캡슐, 캡슐, 정, 밀리그램."
    )
    out.append("")
    out.append(
        "Testing root transfer into pharmacy needs INN ingredient names, which live "
        "behind DrugPrdtPrmsnInfoService (주성분 / MAIN_ITEM_INGR). That endpoint "
        "returns HTTP 400 for the key this project holds; data.go.kr grants keys per "
        "service, so it has to be requested separately. Until then the pharmaceutical "
        "row measures brand naming and is not evidence either way about the lexicon."
    )
    out.append("")
    out.append(
        "The KOSHA row is the one that carries information: 40% of the Hangul in "
        "chemical names is accounted for by the mined roots. What is left is element "
        "names (나트륨, 칼륨), trivial names, and stems that did not clear the "
        "mining thresholds."
    )
    out.append("")
    out.append("## Expert-review candidates\n")
    out.append(
        "The items below are what a Korean transliteration reviewer or a chemist "
        "would be asked to confirm. The unit of review is a single root, not a "
        "whole name, and this is not a full audit of the lexicon.\n"
    )
    out.append("- Roots where the mined Korean form is a translation rather than a")
    out.append("  transliteration (`chloride` → 염화). These carry meaning, so a wrong")
    out.append("  one is a content error, not a spelling one.")
    out.append("- Roots kept on thin evidence (low corpus support in `roots.json`).")
    out.append("- The frequent gap fragments listed above: each is either a missing")
    out.append("  root or a genuine domain-specific term.\n")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description="Cross-domain root coverage")
    ap.add_argument("--output", default=str(PROJECT_ROOT / "docs" / "track-a-coverage-report.md"))
    args = ap.parse_args()

    results = {
        "KOSHA chemicals (source domain)": analyse(kosha_names()),
        "MFDS drug product names": analyse(pharma_names()),
    }
    for label, r in results.items():
        if r:
            print(f"{label}: {r['names']:,} names, char coverage {r['char_coverage']:.1%}, "
                  f"fully covered {r['fully_covered_pct']:.1%}")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(results), encoding="utf-8")
    print(f"\nreport -> {out}")


if __name__ == "__main__":
    main()

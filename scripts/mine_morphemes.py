"""Mine the Korean/English root lexicon from aligned chemical names.

The KOSHA database stores each chemical under both its Korean and English name.
Those pairs are the evidence: if a thousand names contain "chloro" in English
and all of them contain "클로로" in Korean, that correspondence is real.

Method, per candidate English morpheme:
  1. Collect the names that contain it and the names that do not.
  2. Take the Korean substrings common to the positive set.
  3. Keep a Korean form only if it is far more frequent among the positives
     than among the negatives. This is what rejects coincidences: "메틸"
     appears in names without "methyl" too, but rarely.

Candidate morphemes come from IUPAC/Hantzsch-Widman naming rather than being
guessed, so the lexicon stays interpretable.

Usage:
    python scripts/mine_morphemes.py
    python scripts/mine_morphemes.py --db G:/MSDS/data/terminology.db
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.morphology import normalize_en, normalize_ko  # noqa: E402

DEFAULT_DB = Path("G:/MSDS/data/terminology.db")
OUT_PATH = PROJECT_ROOT / "data" / "morphology" / "roots.json"

# Candidate morphemes, grouped by the role they play in a name. Drawn from
# IUPAC substituent prefixes, multiplying prefixes, functional-group suffixes
# and the ring/skeleton stems that dominate an MSDS inventory.
CANDIDATES: dict[str, list[str]] = {
    "prefix": [
        # multiplying
        "mono", "di", "tri", "tetra", "penta", "hexa", "hepta", "octa", "nona", "deca",
        "undeca", "dodeca", "octadeca", "poly", "bis", "tris",
        # halogen and heteroatom substituents
        "fluoro", "chloro", "bromo", "iodo", "perfluoro", "perchloro",
        "hydroxy", "nitro", "nitroso", "amino", "imino", "azo", "diazo", "cyano",
        "thio", "mercapto", "sulfo", "sulfonyl", "sulfinyl", "phospho", "silyl",
        "oxo", "peroxy", "epoxy", "carboxy", "formyl", "acetyl", "benzoyl",
        # alkyl substituents
        "methyl", "ethyl", "propyl", "butyl", "pentyl", "hexyl", "heptyl", "octyl",
        "nonyl", "decyl", "undecyl", "dodecyl", "cetyl", "stearyl", "lauryl",
        "vinyl", "allyl", "phenyl", "benzyl", "tolyl", "naphthyl", "cyclohexyl",
        # stereo / positional
        "iso", "neo", "cyclo", "ortho", "meta", "para", "alpha", "beta", "gamma",
    ],
    "stem": [
        "benzene", "toluene", "xylene", "styrene", "phenol", "cresol", "aniline",
        "naphthalene", "anthracene", "pyridine", "pyrrole", "furan", "thiophene",
        "imidazole", "triazole", "pyrimidine", "purine", "quinoline", "indole",
        "piperazine", "piperidine", "morpholine", "pyrazole", "oxazole",
        "methane", "ethane", "propane", "butane", "pentane", "hexane", "heptane",
        "octane", "nonane", "decane", "ethylene", "propylene", "butylene",
        "acetylene", "butadiene", "isoprene",
        "glycol", "glycerol", "phenyl", "silane", "siloxane", "urea", "melamine",
        "phthalate", "acrylate", "methacrylate", "carbonate", "phosphate",
        "sulfate", "sulfonate", "nitrate", "chloride", "bromide", "iodide",
        "fluoride", "oxide", "hydroxide", "peroxide", "sulfide", "cyanide",
        "acetate", "benzoate", "citrate", "stearate", "laurate", "oleate",
    ],
    "suffix": [
        "ane", "ene", "yne", "ol", "al", "one", "oic", "acid", "amide", "amine",
        "ate", "ite", "ide", "yl", "ic", "ous", "osan", "ose", "ase",
    ],
}

MIN_SUPPORT = 8          # names that must show the pair before it is kept
MIN_PRECISION = 0.45     # share of the morpheme's names carrying the Korean form
MAX_BACKGROUND = 0.25    # share of the other names allowed to carry it anyway


def load_pairs(db_path: Path) -> list[tuple[str, str]]:
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(
            "SELECT name, name_en FROM chemical_terms "
            "WHERE name IS NOT NULL AND name_en IS NOT NULL AND name_en != ''"
        ).fetchall()
    finally:
        conn.close()

    pairs = []
    for ko_raw, en_raw in rows:
        ko, en = normalize_ko(ko_raw), normalize_en(en_raw)
        if ko and en:
            pairs.append((ko, en))
    return pairs


def substrings(text: str, lo: int, hi: int) -> set[str]:
    out = set()
    for size in range(lo, min(hi, len(text)) + 1):
        for i in range(len(text) - size + 1):
            out.add(text[i : i + size])
    return out


def occurs_standalone(name: str, morpheme: str, longer: list[str]) -> bool:
    """True if `morpheme` appears somewhere not already claimed by a longer one.

    "methyl" contains "ethyl". Without this check every methyl- name lands in
    ethyl's positive set and the shared Korean substring collapses to "틸".
    """
    covered = [False] * len(name)
    for big in longer:
        start = 0
        while True:
            i = name.find(big, start)
            if i < 0:
                break
            for j in range(i, i + len(big)):
                covered[j] = True
            start = i + 1
    start = 0
    while True:
        i = name.find(morpheme, start)
        if i < 0:
            return False
        if not any(covered[i : i + len(morpheme)]):
            return True
        start = i + 1


def mine(pairs: list[tuple[str, str]]) -> list[dict]:
    # Korean substring frequency over the whole corpus, for the background rate.
    background: Counter[str] = Counter()
    for ko, _ in pairs:
        background.update(substrings(ko, 1, 6))
    total = len(pairs)

    # Every candidate, so each morpheme knows which longer ones can swallow it.
    all_morphemes = sorted({m for group in CANDIDATES.values() for m in group}, key=len, reverse=True)

    found: list[dict] = []
    seen: set[str] = set()
    for kind, morphemes in CANDIDATES.items():
        for en in morphemes:
            if en in seen:
                continue
            seen.add(en)
            longer = [m for m in all_morphemes if len(m) > len(en) and en in m]
            positives = [ko for ko, en_name in pairs if occurs_standalone(en_name, en, longer)]
            if len(positives) < MIN_SUPPORT:
                continue

            hits: Counter[str] = Counter()
            for ko in positives:
                hits.update(substrings(ko, 1, 6))

            best: list[tuple[str, float, int]] = []
            for form, n in hits.items():
                precision = n / len(positives)
                if precision < MIN_PRECISION:
                    continue
                bg = (background[form] - n) / max(total - len(positives), 1)
                if bg > MAX_BACKGROUND:
                    continue
                # Weight by length: a whole transliteration ("벤젠") is worth more
                # than a syllable of it ("젠"), which survives on its own because
                # unrelated names ("다이페닐디아젠") happen to end the same way.
                best.append((form, (precision - bg) * len(form), n))

            if not best:
                continue
            best.sort(key=lambda item: -item[1])
            top = best[0][1]
            forms = [f for f, sc, _ in best if sc >= top * 0.98][:3]
            found.append(
                {
                    "en": en,
                    "ko": forms,
                    "kind": kind,
                    "count": len(positives),
                    "precision": round(best[0][1], 4),
                }
            )
    return found


def main() -> None:
    ap = argparse.ArgumentParser(description="Mine Korean chemical root lexicon")
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--output", default=str(OUT_PATH))
    args = ap.parse_args()

    db = Path(args.db)
    if not db.exists():
        raise SystemExit(f"database not found: {db}")

    pairs = load_pairs(db)
    print(f"aligned name pairs: {len(pairs):,}")

    roots = mine(pairs)
    roots.sort(key=lambda r: (-r["count"], r["en"]))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "source": "KOSHA chemical_terms, aligned Korean/English names",
                "pairs": len(pairs),
                "min_support": MIN_SUPPORT,
                "min_precision": MIN_PRECISION,
                "max_background": MAX_BACKGROUND,
                "roots": roots,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"roots kept: {len(roots)} -> {out}")

    by_kind: defaultdict[str, int] = defaultdict(int)
    for r in roots:
        by_kind[r["kind"]] += 1
    for kind, n in sorted(by_kind.items()):
        print(f"  {kind:8s} {n}")
    print("\ntop by corpus support:")
    for r in roots[:15]:
        print(f"  {r['en']:14s} -> {'/'.join(r['ko']):18s} {r['count']:>6,} names")


if __name__ == "__main__":
    main()

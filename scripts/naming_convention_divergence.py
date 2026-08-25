"""Do Korean chemical roots survive a move between naming authorities?

Paper 3 mines roots from KOSHA chemical names and asks whether they transfer.
The cosmetics dictionary is the test, because INCI names are built from the
same Latin and Greek stock: if the roots are real, they should appear there.

They do. What does not transfer is the transliteration convention. KOSHA
follows the Korean Chemical Society, which kept the German-derived element
names 나트륨 and 칼륨. The cosmetics dictionary transliterates the English
INCI, giving 소듐 and 포타슘 for the same two elements. A lexicon mined in one
domain then misses names in the other for a reason that has nothing to do with
chemistry.

This matters past the coverage number. A reader who meets sodium lauryl
sulfate on a shampoo bottle and sodium hydroxide on an MSDS is given two
different Korean words for the same element, by two different public bodies,
in the same language.

Element names are measured as whole tokens, which are unambiguous. Prefixes
like 디/다이 are measured only at the start of a name, because as substrings
they match unrelated words (디올, 트리코 …) and would inflate the count.

Usage:
    python scripts/naming_convention_divergence.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

OUT_JSON = PROJECT_ROOT / "docs" / "track-a-convention-divergence.json"

_spec = importlib.util.spec_from_file_location("dc", PROJECT_ROOT / "scripts" / "domain_coverage.py")
dc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dc)

# (English, KOSHA-side form, cosmetics-side form). Whole-token matches.
ELEMENTS = [
    ("sodium", "나트륨", "소듐"),
    ("potassium", "칼륨", "포타슘"),
    ("calcium", "칼슘", "칼슘"),
    ("magnesium", "마그네슘", "마그네슘"),
]

# (English, form A, form B). Matched at the start of a name only.
PREFIXES = [
    ("di-", "디", "다이"),
    ("tri-", "트리", "트라이"),
    ("tetra-", "테트라", "테트라"),
]

# Roots that should transfer if the lexicon describes chemistry rather than
# one registry's house style.
SHARED_ROOTS = ["메틸", "에틸", "프로필", "스테아", "하이드록시", "아크릴"]


def token_rate(names: list[str], form: str) -> tuple[int, float]:
    n = sum(1 for x in names if form in x)
    return n, (n / len(names) if names else 0.0)


def prefix_rate(names: list[str], form: str) -> tuple[int, float]:
    n = sum(1 for x in names if x.startswith(form))
    return n, (n / len(names) if names else 0.0)


def main() -> None:
    kosha = dc.kosha_names()
    cos = dc.cosmetic_names("ko")
    if not kosha or not cos:
        raise SystemExit("need both corpora; run scripts/fetch_kcia_sample.py first")

    print(f"KOSHA chemicals: {len(kosha):,} names")
    print(f"KCIA cosmetics:  {len(cos):,} names\n")

    report: dict = {"kosha_names": len(kosha), "cosmetic_names": len(cos)}

    print("Element names (whole token)")
    print(f"  {'element':12s} {'form':10s} {'KOSHA':>16s} {'cosmetics':>16s}")
    rows = []
    for en, a, b in ELEMENTS:
        entry = {"english": en, "forms": {}}
        for form in dict.fromkeys((a, b)):
            ka, kp = token_rate(kosha, form)
            ca, cp = token_rate(cos, form)
            entry["forms"][form] = {"kosha": ka, "kosha_pct": kp,
                                    "cosmetics": ca, "cosmetics_pct": cp}
            print(f"  {en:12s} {form:10s} {ka:7,d} ({kp:5.2%}) {ca:7,d} ({cp:5.2%})")
        rows.append(entry)
        print()
    report["elements"] = rows

    print("Prefixes (name-initial only)")
    print(f"  {'prefix':10s} {'form':10s} {'KOSHA':>16s} {'cosmetics':>16s}")
    prows = []
    for en, a, b in PREFIXES:
        entry = {"english": en, "forms": {}}
        for form in dict.fromkeys((a, b)):
            ka, kp = prefix_rate(kosha, form)
            ca, cp = prefix_rate(cos, form)
            entry["forms"][form] = {"kosha": ka, "kosha_pct": kp,
                                    "cosmetics": ca, "cosmetics_pct": cp}
            print(f"  {en:10s} {form:10s} {ka:7,d} ({kp:5.2%}) {ca:7,d} ({cp:5.2%})")
        prows.append(entry)
        print()
    report["prefixes"] = prows

    print("Shared roots (whole token) — these should transfer")
    srows = []
    for form in SHARED_ROOTS:
        ka, kp = token_rate(kosha, form)
        ca, cp = token_rate(cos, form)
        srows.append({"form": form, "kosha": ka, "kosha_pct": kp,
                      "cosmetics": ca, "cosmetics_pct": cp})
        print(f"  {form:10s} {ka:7,d} ({kp:5.2%}) {ca:7,d} ({cp:5.2%})")
    report["shared_roots"] = srows

    absent = [e["english"] for e in rows
              for f, v in e["forms"].items()
              if v["kosha"] > 0 and v["cosmetics"] == 0]
    print(f"\nElement forms present in KOSHA and absent from cosmetics: {absent}")
    report["kosha_forms_absent_from_cosmetics"] = absent

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {OUT_JSON}")


if __name__ == "__main__":
    main()

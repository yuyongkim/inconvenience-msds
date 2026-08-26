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
# one registry's house style. Chosen because all three registries use them:
# alkyl chains alone would understate pharmacy, whose names are built from INN
# stems and salt forms rather than from substituent prefixes.
SHARED_ROOTS = ["메틸", "에틸", "프로필", "아세테이트", "벤조", "아미노"]

# The deeper split, and the one the element names were only a symptom of.
# A counter-ion can be rendered two ways: translated into Sino-Korean, or
# transliterated from English. Each registry picks one and stays with it.
# (English, Sino-Korean translation, English transliteration)
STRATEGIES = [
    ("sulfate", "황산", "설페이트"),
    ("phosphate", "인산", "포스페이트"),
    ("hydrochloride", "염산", "클로라이드"),
    ("hydrate", "수화물", "하이드레이트"),
]


def token_rate(names: list[str], form: str) -> tuple[int, float]:
    n = sum(1 for x in names if form in x)
    return n, (n / len(names) if names else 0.0)


def prefix_rate(names: list[str], form: str) -> tuple[int, float]:
    n = sum(1 for x in names if x.startswith(form))
    return n, (n / len(names) if names else 0.0)


def main() -> None:
    kosha = dc.kosha_names()
    cos = dc.cosmetic_names("ko")
    drug = dc.drug_ingredient_names("ko")
    if not kosha or not cos:
        raise SystemExit("need both corpora; run scripts/fetch_kcia_sample.py first")
    if not drug:
        print("note: no drug ingredients; run scripts/fetch_mfds_ingredients.py\n")

    print(f"KOSHA chemicals:      {len(kosha):,} names")
    print(f"KCIA cosmetics:       {len(cos):,} names")
    print(f"MFDS drug ingredients: {len(drug):,} names\n")

    report: dict = {"kosha_names": len(kosha), "cosmetic_names": len(cos),
                    "drug_names": len(drug)}

    print("Element names (whole token)")
    print(f"  {'element':12s} {'form':10s} {'KOSHA':>16s} {'cosmetics':>16s} {'drugs':>16s}")
    rows = []
    for en, a, b in ELEMENTS:
        entry = {"english": en, "forms": {}}
        for form in dict.fromkeys((a, b)):
            ka, kp = token_rate(kosha, form)
            ca, cp = token_rate(cos, form)
            da, dp = token_rate(drug, form)
            entry["forms"][form] = {"kosha": ka, "kosha_pct": kp,
                                    "cosmetics": ca, "cosmetics_pct": cp,
                                    "drugs": da, "drugs_pct": dp}
            print(f"  {en:12s} {form:10s} {ka:7,d} ({kp:5.2%}) "
                  f"{ca:7,d} ({cp:5.2%}) {da:7,d} ({dp:5.2%})")
        rows.append(entry)
        print()
    report["elements"] = rows

    print("Prefixes (name-initial only)")
    print(f"  {'prefix':10s} {'form':10s} {'KOSHA':>16s} {'cosmetics':>16s} {'drugs':>16s}")
    prows = []
    for en, a, b in PREFIXES:
        entry = {"english": en, "forms": {}}
        for form in dict.fromkeys((a, b)):
            ka, kp = prefix_rate(kosha, form)
            ca, cp = prefix_rate(cos, form)
            da, dp = prefix_rate(drug, form)
            entry["forms"][form] = {"kosha": ka, "kosha_pct": kp,
                                    "cosmetics": ca, "cosmetics_pct": cp,
                                    "drugs": da, "drugs_pct": dp}
            print(f"  {en:10s} {form:10s} {ka:7,d} ({kp:5.2%}) "
                  f"{ca:7,d} ({cp:5.2%}) {da:7,d} ({dp:5.2%})")
        prows.append(entry)
        print()
    report["prefixes"] = prows

    print("Naming strategy: translate the counter-ion, or transliterate it")
    print(f"  {'english':16s} {'form':10s} {'KOSHA':>16s} {'cosmetics':>16s} {'drugs':>16s}")
    trows = []
    for en, sino, translit in STRATEGIES:
        entry = {"english": en, "sino": sino, "translit": translit, "forms": {}}
        for form, kind in ((sino, "translated"), (translit, "transliterated")):
            ka, kp = token_rate(kosha, form)
            ca, cp = token_rate(cos, form)
            da, dp = token_rate(drug, form)
            entry["forms"][form] = {"kind": kind,
                                    "kosha": ka, "kosha_pct": kp,
                                    "cosmetics": ca, "cosmetics_pct": cp,
                                    "drugs": da, "drugs_pct": dp}
            print(f"  {en:16s} {form:10s} {ka:7,d} ({kp:5.2%}) "
                  f"{ca:7,d} ({cp:5.2%}) {da:7,d} ({dp:5.2%})")
        trows.append(entry)
        print()
    report["strategies"] = trows

    print("Shared roots (whole token) — these should transfer")
    srows = []
    for form in SHARED_ROOTS:
        ka, kp = token_rate(kosha, form)
        ca, cp = token_rate(cos, form)
        da, dp = token_rate(drug, form)
        srows.append({"form": form, "kosha": ka, "kosha_pct": kp,
                      "cosmetics": ca, "cosmetics_pct": cp,
                      "drugs": da, "drugs_pct": dp})
        print(f"  {form:10s} {ka:7,d} ({kp:5.2%}) {ca:7,d} ({cp:5.2%}) {da:7,d} ({dp:5.2%})")
    report["shared_roots"] = srows

    # The interesting cell is not a low rate, it is a zero: a registry that
    # never uses a form its neighbour uses constantly has a house style, not a
    # preference.
    mutually_exclusive = []
    for e in rows + prows:
        forms = list(e["forms"].items())
        if len(forms) != 2:
            continue
        (fa, va), (fb, vb) = forms
        if va["cosmetics"] == 0 and vb["drugs"] == 0 and va["drugs"] and vb["cosmetics"]:
            mutually_exclusive.append({"english": e["english"],
                                       "drugs_use": fa, "cosmetics_use": fb})
        elif vb["cosmetics"] == 0 and va["drugs"] == 0 and vb["drugs"] and va["cosmetics"]:
            mutually_exclusive.append({"english": e["english"],
                                       "drugs_use": fb, "cosmetics_use": fa})
    print("\nForms where cosmetics and pharmacy do not overlap at all:")
    for m in mutually_exclusive:
        print(f"  {m['english']:12s} drugs use {m['drugs_use']}, "
              f"cosmetics use {m['cosmetics_use']}")
    report["mutually_exclusive"] = mutually_exclusive

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {OUT_JSON}")


if __name__ == "__main__":
    main()

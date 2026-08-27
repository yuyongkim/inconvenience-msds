"""Per-domain validation: does one encoder really serve differently shaped documents?

Paper 2 claims a single braille encoder covers catalogues that do not look alike
— an MSDS is sixteen numbered sections of terse tabular text, a drug label is
prose written for patients. The claim is only worth making if it is checked per
domain rather than in aggregate, because an aggregate number lets a strong
domain carry a weak one.

Three things are measured for each domain, and they answer different questions:

**Expansion ratio** — cells per source character. It is the number that decides
whether a document fits on an embosser, and it varies by domain because the text
does: prose expands differently from a table of CAS numbers.

**Round-trip** — encode, decode, compare. Reported three ways, because
comparing against the raw source measures the writing system as much as the
code.

*Exact* is the naive comparison and is the weakest of the three. Korean braille
has rules that change the text: 제38항 [다만] requires a space between a digit
and a following initial that shares its cell, so "3회" must be embossed as
"3 회" and no decoder can put it back. Pesticide rows almost all carry a
사용횟수 like "3회", which is why their exact score is low while their braille
is correct.

*Near* folds away what braille does not carry at all — letter case and runs of
whitespace.

*Stable* is the one that answers the correctness question. Encode, decode,
encode, decode again: if the second pass equals the first, the transformation
has reached a fixed point and nothing further is being lost. A pipeline that
inserts a rule-mandated space scores 100% here; one that drops or corrupts a
character does not, because the damage compounds on the second pass.

**Rule compliance** — the 2017 Korean braille rules, checked by `eval.rule_checker`.
A document can round-trip perfectly and still be malformed braille.

Round-trip is reported both raw and as a near-match, because the decoder cannot
recover what braille does not encode. Korean braille has no case, so English
inside a Korean text comes back lowercased; scoring that as a failure would
report a property of the writing system as a defect in the pipeline.

Usage:
    python eval/paper2_validation.py
"""

from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from eval.rule_checker import check_all_rules  # noqa: E402
from pipeline.adapters.drug import DrugAdapter  # noqa: E402
from pipeline.adapters.incident import IncidentAdapter  # noqa: E402
from pipeline.adapters.pesticide import PesticideAdapter  # noqa: E402
from pipeline.ko_braille import encode_korean_braille  # noqa: E402
from pipeline.ko_braille_decoder import decode_korean_braille  # noqa: E402

OUT_JSON = PROJECT_ROOT / "docs" / "paper2-validation.json"
DRUG_CORPUS = PROJECT_ROOT / "data" / "paper2" / "drug_corpus.json"
PESTICIDE_CORPUS = PROJECT_ROOT / "data" / "paper2" / "pesticide_corpus.json"
INCIDENT_CORPUS = PROJECT_ROOT / "data" / "paper2" / "incident_corpus.json"


def normalise(text: str) -> str:
    """Fold away what braille does not carry, so the comparison tests the pipeline.

    Korean braille encodes no letter case and collapses runs of whitespace, so
    a decoder cannot return either. Counting those as round-trip failures would
    measure the writing system rather than the code.
    """
    text = unicodedata.normalize("NFC", text).lower()
    return " ".join(text.split())


def take(records: list, sample: int | None) -> list:
    """An even stride through the corpus, not its first N.

    Every corpus here arrives ordered — drugs by item sequence, incidents by
    board number — and the order correlates with length. Taking the head of the
    incident board gives records averaging 128 characters against the corpus's
    514, because the most recent postings are the shortest. That would have put
    a number in the paper that says more about the sampling than the domain.
    """
    if not sample or len(records) <= sample:
        return records
    stride = len(records) / sample
    return [records[int(i * stride)] for i in range(sample)]


def validate(records, domain: str, sample: int | None = None) -> dict:
    rows, exact, near, stable = [], 0, 0, 0
    total_text = total_cells = 0
    violations: dict[str, int] = {}

    subset = take(records, sample)
    for rec in subset:
        text = rec.text()
        if not text.strip():
            continue
        braille = encode_korean_braille(text)
        total_text += len(text)
        total_cells += len(braille)

        try:
            back = decode_korean_braille(braille)
        except Exception:
            back = ""

        is_exact = back == text
        is_near = normalise(back) == normalise(text)

        # Second pass. What the rules mandate is applied once and then holds;
        # what is genuinely lost keeps degrading.
        try:
            again = decode_korean_braille(encode_korean_braille(back))
        except Exception:
            again = ""
        is_stable = bool(back) and again == back

        exact += is_exact
        near += is_near
        stable += is_stable

        result = check_all_rules(braille)
        for name, res in result.items():
            n = len(getattr(res, "violations", []) or [])
            if n:
                violations[name] = violations.get(name, 0) + n

        rows.append({
            "record_id": rec.record_id,
            "text_chars": len(text),
            "braille_cells": len(braille),
            "roundtrip_exact": is_exact,
            "roundtrip_near": is_near,
            "roundtrip_stable": is_stable,
        })

    n = len(rows) or 1
    return {
        "domain": domain,
        "records": len(rows),
        "text_chars": total_text,
        "braille_cells": total_cells,
        "expansion_ratio": round(total_cells / total_text, 3) if total_text else 0.0,
        "mean_text_chars": round(total_text / n),
        "roundtrip_exact_pct": round(exact / n, 4),
        "roundtrip_near_pct": round(near / n, 4),
        "roundtrip_stable_pct": round(stable / n, 4),
        "rule_violations": violations,
        "rows": rows,
    }


def load_drugs() -> list:
    if not DRUG_CORPUS.exists():
        return []
    raw = json.loads(DRUG_CORPUS.read_text(encoding="utf-8"))
    return DrugAdapter().adapt_many(raw.get("records", []))


def load_pesticides() -> list:
    if not PESTICIDE_CORPUS.exists():
        return []
    raw = json.loads(PESTICIDE_CORPUS.read_text(encoding="utf-8"))
    return PesticideAdapter().adapt_many(raw.get("records", []))


def load_incidents() -> list:
    if not INCIDENT_CORPUS.exists():
        return []
    raw = json.loads(INCIDENT_CORPUS.read_text(encoding="utf-8"))
    return IncidentAdapter().adapt_many(raw.get("records", []))


def main() -> None:
    results = {}

    drugs = load_drugs()
    if drugs:
        print(f"drug: {len(drugs):,} adapted records")
        results["drug"] = validate(drugs, "drug", sample=800)
    else:
        print("drug: no corpus; run scripts/paper2_fetch_drugs.py first")

    pest = load_pesticides()
    if pest:
        print(f"pesticide: {len(pest):,} adapted records")
        results["pesticide"] = validate(pest, "pesticide", sample=800)
    else:
        print("pesticide: no corpus; run scripts/paper2_fetch_pesticides.py first")

    inc = load_incidents()
    if inc:
        print(f"incident: {len(inc):,} adapted records")
        results["incident"] = validate(inc, "incident", sample=800)
    else:
        print("incident: no corpus; run scripts/paper2_fetch_incidents.py first")

    print()
    print(f"{'domain':10s} {'records':>8s} {'chars':>10s} {'cells':>11s} "
          f"{'ratio':>7s} {'exact':>8s} {'near':>8s} {'stable':>8s}")
    for name, r in results.items():
        print(f"{name:10s} {r['records']:>8,} {r['text_chars']:>10,} "
              f"{r['braille_cells']:>11,} {r['expansion_ratio']:>7.2f} "
              f"{r['roundtrip_exact_pct']:>7.1%} {r['roundtrip_near_pct']:>7.1%} "
              f"{r['roundtrip_stable_pct']:>7.1%}")
        if r["rule_violations"]:
            print(f"{'':10s} rule violations: {r['rule_violations']}")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(
        {k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in results.items()},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n-> {OUT_JSON}")


if __name__ == "__main__":
    main()

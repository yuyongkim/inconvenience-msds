"""Join the three paper-2 catalogues back to the paper-1 chemical catalogue.

The claim this measures is the one the earlier paper could only gesture at: an
accident case describes a hazard that a safety data sheet also describes, and if
both are in braille under the same rules then a reader who meets one can reach
the other. That is only true if the two can actually be joined, and whether they
can is an empirical question about how the registers write chemical names.

Matching is done on Korean names, and deliberately not fuzzily. Two strings that
merely look similar are not the same substance — 염화메틸 and 염화메틸렌 differ
by two characters and by a great deal of toxicology — so a link is recorded only
when a catalogue name occurs verbatim in the target text. The cost is recall,
and recall is the right thing to spend here: a cross-reference that sends a
reader to the wrong data sheet is worse than one that sends them nowhere.

Names shorter than three characters are dropped. The catalogue contains entries
like 물 and 납, and matching those against free prose produces links on every
sentence that happens to contain the syllable.

Usage:
    python scripts/paper2_cross_reference.py
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.adapters.drug import DrugAdapter  # noqa: E402
from pipeline.adapters.incident import IncidentAdapter  # noqa: E402
from pipeline.adapters.pesticide import PesticideAdapter  # noqa: E402

DB = "G:/MSDS/data/terminology.db"
CORPORA = PROJECT_ROOT / "data" / "paper2"
OUT = PROJECT_ROOT / "docs" / "paper2-cross-reference.json"

# 물, 납, 은 and the like. Three characters is where a Korean chemical name
# stops being a word that free prose uses for something else.
MIN_NAME = 3

# The catalogue writes "벤젠 (Benzene)" and sometimes appends a synonym block.
# Only the leading Korean name is a name; the rest is annotation.
LEAD_KO = re.compile(r"^([가-힣0-9\-,'·\s]+?)\s*[(\[]")
HANGUL = re.compile(r"[가-힣]")


def catalogue_en() -> dict[str, str]:
    """Lower-cased English chemical name -> CAS, from the same catalogue.

    The Korean side of the join fails for drugs for a reason that is not about
    braille at all: the approval register writes its active ingredient in
    English. Matching the English gives the honest measure of whether the two
    catalogues *can* be joined, as against whether they can be joined in one
    language.
    """
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    out: dict[str, str] = {}
    for name_en, cas in con.execute(
            "select name_en, cas_no from chemical_terms where name_en is not null"):
        key = (name_en or "").strip().lower()
        # Five characters keeps out the register's stub entries ("oil", "wax")
        # that would match an ingredient list on the wrong word.
        if len(key) >= 5:
            out.setdefault(key, cas or "")
    con.close()
    return out


def english_hits(text: str, names_en: dict[str, str]) -> set[str]:
    """Catalogue English names appearing in a slash- or comma-separated field.

    The register writes ingredients as a list — "Aspirin/Magnesium Carbonate" —
    so splitting on the separators and looking each part up exactly is both
    cheaper and stricter than scanning for substrings.
    """
    out = set()
    for part in re.split(r"[/,;+]| and ", text):
        key = re.sub(r"\s+", " ", part).strip().lower()
        key = re.sub(r"\s*\d+(\.\d+)?\s*%?$", "", key).strip()
        if key in names_en:
            out.add(key)
    return out


def catalogue() -> dict[str, tuple[str, str]]:
    """Korean chemical name -> (CAS, English name), from the paper-1 catalogue."""
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    out: dict[str, tuple[str, str]] = {}
    for name, cas, name_en in con.execute(
            "select name, cas_no, name_en from chemical_terms"):
        if not name:
            continue
        m = LEAD_KO.match(name)
        ko = (m.group(1) if m else name).strip()
        if len(ko) < MIN_NAME or not HANGUL.search(ko):
            continue
        # Keep the first spelling seen; the catalogue repeats substances across
        # sources and the duplicates carry the same CAS.
        out.setdefault(ko, (cas or "", name_en or ""))
    con.close()
    return out


def build_matcher(names: dict[str, tuple[str, str]]):
    """One alternation over every catalogue name, longest first.

    Longest-first matters: 염화메틸렌 must win over 염화메틸 where both could
    match, or the join reports the wrong substance rather than no substance.
    """
    ordered = sorted(names, key=len, reverse=True)
    return re.compile("|".join(re.escape(n) for n in ordered))


def matches_in(text: str, matcher) -> set[str]:
    """Catalogue names occurring as whole words, not as fragments.

    Korean does not space compounds, so a bare `findall` reports 프로필 inside
    프로필렌 and 톨루엔 inside 트리클로로톨루엔. Requiring that neither
    neighbouring character be Hangul is crude but it is the boundary Korean
    actually offers, and it errs towards missing a link rather than inventing
    one.
    """
    out = set()
    for m in matcher.finditer(text):
        before = text[m.start() - 1] if m.start() else ""
        after = text[m.end()] if m.end() < len(text) else ""
        if HANGUL.match(before) or HANGUL.match(after):
            continue
        out.add(m.group(0))
    return out


# Sections that say what the record *is*. A name here identifies the substance;
# the same name in 상호작용 or 사고 경위 is a mention of something else the
# record talks about. Both are worth having and they are not the same claim, so
# they are counted separately.
IDENTITY_SECTIONS = {"주성분", "품목명", "성분"}

# An accident case has no field that names a substance; whatever chemistry it
# carries is inside the narrative. So it has no identity section, and its number
# below is a mention count by construction rather than by accident.

# Sections that describe the target of an application rather than its content.
# 아카시아 and 알로에 are in the chemical catalogue and are also crops; a match
# in 작물 is the crop, every time.
NOT_CHEMICAL_SECTIONS = {"작물", "병해충 또는 잡초"}


def link(records, matcher, names, names_en=None, sample: int | None = None) -> dict:
    subset = records[:sample] if sample else records
    linked = identified = identified_en = 0
    hits: dict[str, int] = {}
    examples: list[dict] = []
    for rec in subset:
        strong: set[str] = set()
        strong_en: set[str] = set()
        found: set[str] = set()
        for sec in rec.sections:
            if sec.title in NOT_CHEMICAL_SECTIONS:
                continue
            got = matches_in(sec.text, matcher)
            found |= got
            if sec.title in IDENTITY_SECTIONS:
                strong |= got
                if names_en:
                    strong_en |= english_hits(sec.text, names_en)
        identified_en += bool(strong_en)
        if not (found or strong_en):
            continue
        linked += 1
        identified += bool(strong)
        for f in found:
            hits[f] = hits.get(f, 0) + 1
        if len(examples) < 8:
            examples.append({
                "record_id": rec.record_id,
                "name": rec.name[:60],
                "identified": sorted(strong)[:5],
                "chemicals": [{"ko": f, "cas": names[f][0], "en": names[f][1]}
                              for f in sorted(found)[:5]],
            })
    n = len(subset) or 1
    return {
        "records": len(subset),
        "linked": linked,
        "linked_pct": round(linked / n, 4),
        "identified": identified,
        "identified_pct": round(identified / n, 4),
        "identified_en": identified_en,
        "identified_en_pct": round(identified_en / n, 4),
        "distinct_chemicals": len(hits),
        "top": sorted(hits.items(), key=lambda kv: -kv[1])[:15],
        "examples": examples,
    }


def load(key: str, adapter_cls) -> list:
    path = CORPORA / f"{key}_corpus.json"
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return adapter_cls().adapt_many(raw.get("records", []))


def main() -> None:
    names = catalogue()
    names_en = catalogue_en()
    print(f"catalogue: {len(names):,} Korean names (>= {MIN_NAME} chars), "
          f"{len(names_en):,} English names")
    matcher = build_matcher(names)

    results = {}
    for key, cls in [("incident", IncidentAdapter),
                     ("drug", DrugAdapter),
                     ("pesticide", PesticideAdapter)]:
        records = load(key, cls)
        if not records:
            print(f"{key}: no corpus, skipped")
            continue
        results[key] = link(records, matcher, names, names_en)
        r = results[key]
        print(f"{key:10s} {r['linked']:>6,}/{r['records']:,} mention "
              f"({r['linked_pct']:>5.1%})  "
              f"KO-id {r['identified_pct']:>5.1%}  "
              f"EN-id {r['identified_en_pct']:>5.1%}  "
              f"{r['distinct_chemicals']:,} distinct")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "catalogue": {"source": "KOSHA chemical_terms (paper 1)",
                      "korean_names": len(names),
                      "min_name_length": MIN_NAME},
        "method": "verbatim occurrence of a catalogue name, bounded so a name "
                  "inside a longer Korean compound does not count; longest match "
                  "wins; no fuzzy matching. `identified` counts links found in a "
                  "section that says what the record is; `linked` also counts "
                  "mentions elsewhere in the record.",
        "identity_sections": sorted(IDENTITY_SECTIONS),
        "excluded_sections": sorted(NOT_CHEMICAL_SECTIONS),
        "domains": results,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()

"""Korean drug ingredient names, the domain paper 3 could not measure.

Paper 3 reports 1.5% root coverage for pharmaceuticals and says in Section 4.3
that this measures the wrong strings: `DrbEasyDrugInfoService` returns product
names, and 활명수 has no Latin root to find. The ingredient names live in the
drug approval service, which needed a separately authorised key.

That key exists and works, and it works directly. An earlier version of this
script went through the chemical information service that already held it, on
the theory that data.go.kr was refusing calls from here. It was not: the key in
.env is stored quoted and split across two lines, and a line-at-a-time parser
was truncating it into something the portal rejects by name. `scripts/keys.py`
reads it properly and the register answers directly.

Two fields carry what we need, in two scripts:

    ITEM_NAME       보령아스트릭스캡슐100밀리그람(아스피린)
    ITEM_INGR_NAME  Aspirin Enteric Granules

Korean generic drugs print the active ingredient in parentheses after the
product name, and the English ingredient comes as its own field. Together they
give the aligned pair the lexicon is measured against — the same shape as the
cosmetics dictionary, arrived at differently.

The approval API has no "list everything" call, only substring search on the
product name, so this sweeps dosage-form words that nearly every product name
contains (정, 캡슐, 주사…) and dedupes across them.

Usage:
    python scripts/fetch_mfds_ingredients.py [--per-term 30] [--delay 0.4]
"""

from __future__ import annotations

import argparse
import json
import re
import time
import sys
from pathlib import Path

import requests
import urllib3

sys.path.insert(0, str(Path(__file__).resolve().parent))
import keys  # noqa: E402

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = PROJECT_ROOT / "data" / "pharma" / "mfds_ingredients.json"

SERVICE = ("https://apis.data.go.kr/1471000/DrugPrdtPrmsnInfoService07/"
           "getDrugPrdtPrmsnInq07")
PAGE_SIZE = 100           # the portal's per-request ceiling

# Dosage-form and unit words. Between them they appear in nearly every Korean
# product name, so sweeping them approximates a full listing that the API does
# not offer. Ordered by how many products each matches.
TERMS = ["정", "밀리그램", "산", "캡슐", "주", "액", "시럽", "점안",
         "주사", "과립", "크림", "밀리그람", "연고"]

# The active ingredient, printed in parentheses after the product name.
PAREN = re.compile(r"\(([^()]{2,80})\)")

# Parentheticals that are not ingredients: export names, dosage restatements.
NOT_INGREDIENT = re.compile(
    r"^(수출\s*명|수출명|서방|장용|당의|필름코팅|프리믹스)"
    r"|^[\d.,%\s]+$"
    r"|^[A-Za-z0-9 ,.\-]+$"          # pure Latin: that is the English name
)
HANGUL = re.compile(r"[가-힣]")


def fetch(key: str, term: str, page: int, attempts: int = 4) -> dict | None:
    """One page, retried. Returns None only if every attempt failed.

    The portal occasionally answers a transient application error under load. An
    earlier version treated one failure as "this term is exhausted" and
    abandoned the remaining twelve terms, which cost most of a run.
    """
    params = {"serviceKey": key, "item_name": term, "pageNo": page,
              "numOfRows": PAGE_SIZE, "type": "json"}
    for attempt in range(attempts):
        try:
            d = requests.get(SERVICE, params=params, timeout=120,
                             verify=False).json()
            items = (d.get("body") or {}).get("items", [])
            if isinstance(items, dict):
                items = items.get("item", [])
            if isinstance(items, dict):
                items = [items]
            return {"items": [i for i in items if isinstance(i, dict)]}
        except Exception:
            if attempt < attempts - 1:
                time.sleep(2 ** attempt)
    return None


def load_existing() -> tuple[dict[str, str], set[str]]:
    """Previous results, so a short run never destroys a long one."""
    if not OUT_JSON.exists():
        return {}, set()
    try:
        d = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}, set()
    return ({p["ko"]: p["en"] for p in d.get("pairs", [])},
            set(d.get("korean_only", [])))


def korean_ingredient(item_name: str) -> str | None:
    """The Hangul ingredient inside the product name's parentheses, if any."""
    for cand in PAREN.findall(item_name or ""):
        s = cand.strip()
        if len(s) < 3 or NOT_INGREDIENT.search(s) or not HANGUL.search(s):
            continue
        return s
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-term", type=int, default=30,
                    help="pages to pull per search term (50 products each)")
    ap.add_argument("--delay", type=float, default=0.4)
    args = ap.parse_args()

    seen_items: set[str] = set()
    pairs, ko_only = load_existing()
    if pairs:
        print(f"carrying forward {len(pairs):,} pairs from a previous run\n")
    products = 0
    calls = 0
    failures = 0

    key = keys.service_key()
    for term in TERMS:
        got_for_term = 0
        misses = 0
        for page in range(1, args.per_term + 1):
            d = fetch(key, term, page)
            calls += 1
            if d is None:
                failures += 1
                misses += 1
                if misses >= 3:      # three dead pages: this term is done
                    break
                continue
            misses = 0
            items = d.get("items") or []
            if not items:
                break
            for it in items:
                seq = it.get("ITEM_SEQ")
                if seq in seen_items:
                    continue
                seen_items.add(seq)
                products += 1
                ko = korean_ingredient(it.get("ITEM_NAME", ""))
                if not ko:
                    continue
                en = (it.get("ITEM_INGR_NAME") or "").strip()
                got_for_term += 1
                if en:
                    pairs.setdefault(ko, en)
                else:
                    ko_only.add(ko)
            time.sleep(args.delay)
        print(f"  {term:8s} +{got_for_term:5d} named  "
              f"(running: {products:,} products, {len(pairs):,} pairs)")

    ko_only -= set(pairs)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({
        "source": "MFDS 의약품 제품 허가정보 (DrugPrdtPrmsnInfoService07), "
                  "via the chemip drug service",
        "method": "Korean ingredient from the ITEM_NAME parenthetical; "
                  "English from ITEM_INGR_NAME",
        "search_terms": TERMS,
        "api_calls": calls,
        "products_seen": products,
        "pairs": [{"ko": k, "en": v} for k, v in sorted(pairs.items())],
        "korean_only": sorted(ko_only),
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n{products:,} distinct products over {calls} calls")
    print(f"{len(pairs):,} Korean/English ingredient pairs")
    print(f"{len(ko_only):,} Korean ingredient names without an English counterpart")
    print("\nsample pairs:")
    for ko in sorted(pairs)[:8]:
        print(f"   {ko:28s} {pairs[ko][:44]}")
    print(f"\n-> {OUT_JSON}")


if __name__ == "__main__":
    main()

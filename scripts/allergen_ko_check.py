"""Check the summariser's Korean allergen names against the official dictionary.

`ingredient_summary.ALLERGEN_KO` was written by transliterating the EU list by
hand. That is fine for a demonstration and not fine for a label reader: if the
Korean spelling is off by one syllable, an allergen on a Korean-market bottle
is read out as an ordinary ingredient and the user is told nothing is there.
A silent miss is the worst failure this component has.

So this looks each of the 26 EU-labelled fragrance allergens up in the Korean
Cosmetic Association dictionary, which is the body that decides the Korean
spelling, and reports three things: which of our names are right, which are
wrong, and which of the 26 we never had a Korean name for at all.

Twenty-six lookups, one per allergen. Nothing is cached to disk beyond the
comparison, in line with the dictionary's terms.

Usage:
    python scripts/allergen_ko_check.py
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.ingredient_summary import ALLERGEN_KO, EU_LABELLED_ALLERGENS  # noqa: E402

OUT_JSON = PROJECT_ROOT / "docs" / "track-b-allergen-ko-check.json"

SEARCH = "https://kcia.or.kr/cid/search/ingd_list.php?skind=ALL&sword="
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; kosha-braille-research/1.0)",
    "Referer": "https://kcia.or.kr/cid/main/",
}
ROW = re.compile(
    r'<td class="left"><a href="ingd_view\.php\?no=\d+"><p><b>(.*?)</b></p></a></td>\s*'
    r'<td class="left"><a href="ingd_view\.php\?no=\d+"><p>(.*?)</p></a></td>',
    re.S,
)
TAG = re.compile(r"<[^>]+>")


def lookup(english: str) -> str | None:
    """The Korean name the dictionary gives for an exact English INCI match."""
    url = SEARCH + urllib.parse.quote(english)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None
    for ko, en in ROW.findall(html):
        ko, en = TAG.sub("", ko).strip(), TAG.sub("", en).strip()
        if en.lower() == english.lower():
            return ko
    return None


def main() -> None:
    ours = {v: k for k, v in ALLERGEN_KO.items()}  # english -> our Korean

    rows, correct, wrong, missing, unlisted = [], [], [], [], []
    for en in sorted(EU_LABELLED_ALLERGENS):
        official = lookup(en)
        mine = ours.get(en)
        if official is None:
            status = "not-in-dictionary"
            unlisted.append(en)
        elif mine is None:
            status = "we-had-none"
            missing.append((en, official))
        elif mine == official:
            status = "match"
            correct.append(en)
        else:
            status = "mismatch"
            wrong.append((en, mine, official))
        rows.append({"english": en, "ours": mine, "official": official, "status": status})
        print(f"  {en:46s} ours={mine or '-':16s} official={official or '-':16s} {status}")
        time.sleep(0.7)

    n = len(EU_LABELLED_ALLERGENS)
    print(f"\n{n} EU-labelled allergens")
    print(f"  correct in our table : {len(correct)}")
    print(f"  wrong spelling       : {len(wrong)}")
    print(f"  we had no Korean name: {len(missing)}")
    print(f"  not found in dictionary: {len(unlisted)}")
    if wrong:
        print("\nMismatches — each of these is a silent miss on a Korean label:")
        for en, mine, off in wrong:
            print(f"  {en}: we wrote {mine}, the dictionary says {off}")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({
        "source": "대한화장품협회 화장품성분사전 (https://kcia.or.kr/cid)",
        "allergen_count": n,
        "correct": len(correct),
        "mismatched": [{"english": e, "ours": m, "official": o} for e, m, o in wrong],
        "we_had_none": [{"english": e, "official": o} for e, o in missing],
        "not_in_dictionary": unlisted,
        "rows": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n-> {OUT_JSON}")


if __name__ == "__main__":
    main()

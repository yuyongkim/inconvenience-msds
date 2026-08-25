"""Sample the KCIA cosmetic ingredient dictionary for a coverage measurement.

Paper 3 claims chemical roots transfer across domains, and cosmetics is the
domain that would test it: INCI names are built from the same Latin and Greek
stock as industrial chemicals, and the Korean side of the dictionary is a
transliteration of it. Paper 4's summariser also needs Korean ingredient names,
since Korean-market labels do not print INCI in English.

Two constraints shape this script.

The dictionary's terms of use (Article 9(2)) vest copyright in the association
and forbid reproducing or redistributing what you obtain from the service for
commercial purposes. So this fetches a sample into a gitignored cache and
nothing else: the repository carries derived statistics, never the entries.
Republishing the pairs would need the association's prior consent, which is a
letter to write, not a flag to set.

The second is their server. The dictionary holds roughly 24,900 entries at ten
per page. Fetching every page would be 2,500 requests for a number that a
sample answers just as well, so this walks a fixed stride with a delay and
takes about a thousand.

Usage:
    python scripts/fetch_kcia_sample.py [--pages 150] [--delay 0.7]
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE = PROJECT_ROOT / "data" / "kcia_cache" / "sample.json"

BASE = "https://kcia.or.kr/cid/search/ingd_list.php?skind=ALL&sword="
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; kosha-braille-research/1.0)",
    "Referer": "https://kcia.or.kr/cid/main/",
}

# One <tr> of the results table: code, Korean name, English name, CAS, old name.
ROW = re.compile(
    r"<tr>\s*<td><p>(\d+)</p></td>\s*"
    r'<td class="left"><a href="ingd_view\.php\?no=\d+"><p><b>(.*?)</b></p></a></td>\s*'
    r'<td class="left"><a href="ingd_view\.php\?no=\d+"><p>(.*?)</p></a></td>\s*'
    r"<td><p>(.*?)</p></td>\s*<td><p>(.*?)</p></td>",
    re.S,
)
TAG = re.compile(r"<[^>]+>")


def fetch_page(page: int) -> list[dict]:
    url = f"{BASE}&page={page}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", "replace")
    out = []
    for code, ko, en, cas, old in ROW.findall(html):
        clean = [TAG.sub("", f).strip() for f in (ko, en, cas, old)]
        out.append({"code": int(code), "ko": clean[0], "en": clean[1],
                    "cas": clean[2], "old_ko": clean[3]})
    return out


def total_pages() -> int:
    """Highest ingredient code, divided by the ten rows a page holds."""
    first = fetch_page(1)
    return (max(r["code"] for r in first) // 10) + 1 if first else 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=150,
                    help="how many pages to sample, spread evenly")
    ap.add_argument("--delay", type=float, default=0.7,
                    help="seconds between requests")
    args = ap.parse_args()

    pages = total_pages()
    if not pages:
        raise SystemExit("could not read the first page; the dictionary may have moved")
    stride = max(pages // args.pages, 1)
    wanted = list(range(1, pages + 1, stride))[: args.pages]
    print(f"dictionary spans ~{pages} pages; sampling {len(wanted)} at stride {stride}")

    rows: list[dict] = []
    failed = 0
    for i, p in enumerate(wanted, 1):
        try:
            rows.extend(fetch_page(p))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            failed += 1
        if i % 25 == 0 or i == len(wanted):
            print(f"  {i}/{len(wanted)} pages, {len(rows)} entries")
        time.sleep(args.delay)

    if failed:
        print(f"note: {failed} pages failed and were skipped")

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps({
        "source": "대한화장품협회 화장품성분사전 (https://kcia.or.kr/cid)",
        "licence_note": "Terms Art. 9(2): copyright rests with the association; "
                        "commercial reproduction or redistribution is prohibited. "
                        "This cache is local-only and gitignored. Publish derived "
                        "statistics, not entries.",
        "pages_in_dictionary": pages,
        "pages_sampled": len(wanted),
        "stride": stride,
        "entries": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {CACHE} ({len(rows)} entries)")


if __name__ == "__main__":
    main()

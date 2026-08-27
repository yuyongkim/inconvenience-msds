"""Build the paper 2 incident corpus from KOSHA's domestic accident-case board.

This is the third domain, and it is here because the first two are not enough to
support the claim. Drug labels and pesticide registrations are both *records*:
somebody filled in fields, and the adapter's job is to read those fields in a
sensible order. If the encoder only ever meets records, "one encoder covers
differently shaped catalogues" is a weaker statement than it sounds, because the
shapes are not that different.

Accident cases are not records. `contents` is a free paragraph written by an
investigator — a date, a place, a sequence of events, ending in an injury. It
carries the things prose carries and forms do not: dates written as
"2026. 2. 27.(금) 20:57", measurements mid-sentence, clause after clause without
a field boundary to lean on. That is the case the braille rules are hardest on,
so it is the case worth measuring.

6,362 cases, 1,000 to a page, seven requests. The service allows 30 requests a
second and this needs seven, so the delay below is courtesy rather than
necessity.

Usage:
    python scripts/paper2_fetch_incidents.py [--target 6362] [--check]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests
import urllib3

sys.path.insert(0, str(Path(__file__).resolve().parent))
import keys  # noqa: E402

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "data" / "paper2" / "incident_corpus.json"

URL = "https://apis.data.go.kr/B552468/disaster_api02/getdisaster_api02"

# Fixed by the service, and not guessable: the value is given only in the
# activity guide attached to the dataset page, not in the parameter list.
CALL_API_ID = "1060"

PAGE = 1000


def fetch(key: str, page: int, rows: int, attempts: int = 3) -> tuple[list, int]:
    params = {
        "serviceKey": key,
        "callApiId": CALL_API_ID,
        "pageNo": page,
        "numOfRows": rows,
    }
    for attempt in range(attempts):
        try:
            r = requests.get(URL, params=params, timeout=120, verify=False)
            d = r.json()
            header = d.get("header", {})
            code = header.get("resultCode")
            if code not in ("00", None):
                raise SystemExit(f"{code}: {header.get('resultMsg')}")
            body = d.get("body", {})
            items = body.get("items", {}).get("item", [])
            if isinstance(items, dict):
                items = [items]
            return items, int(body.get("totalCount") or 0)
        except SystemExit:
            raise
        except Exception:
            if attempt < attempts - 1:
                time.sleep(2 ** attempt)
    return [], 0


def check(key: str) -> None:
    """One call, printed plainly. Run this before blaming the collection code."""
    items, total = fetch(key, 1, 1)
    print(f"total cases: {total:,}")
    if items:
        it = items[0]
        print(f"  boardno : {it.get('boardno')}")
        print(f"  business: {it.get('business')}")
        print(f"  keyword : {it.get('keyword')}")
        print(f"  contents: {(it.get('contents') or '')[:120]}...")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=0, help="0 collects the board")
    ap.add_argument("--delay", type=float, default=0.5)
    ap.add_argument("--check", action="store_true", help="one call, then stop")
    args = ap.parse_args()

    key = keys.service_key()
    if args.check:
        check(key)
        return

    rows: list[dict] = []
    seen: set[str] = set()
    page = 1
    total = 0
    while True:
        got, total = fetch(key, page, PAGE)
        if not got:
            break
        for it in got:
            board = it.get("boardno")
            if board and board not in seen:
                seen.add(board)
                rows.append(it)
        print(f"  page {page}: {len(rows):,}/{total:,}", flush=True)
        if args.target and len(rows) >= args.target:
            break
        if len(rows) >= total or len(got) < PAGE:
            break
        page += 1
        time.sleep(args.delay)

    businesses: dict[str, int] = {}
    for r in rows:
        b = (r.get("business") or "").strip() or "(미분류)"
        businesses[b] = businesses.get(b, 0) + 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": "한국산업안전보건공단 국내재해사례 게시판 "
                  "(data.go.kr 15121001, disaster_api02, callApiId=1060)",
        "board_total": total,
        "collected": len(rows),
        "by_business": businesses,
        "note": "contents is investigator prose, not a filled-in form; that is "
                "why this domain is in the paper.",
        "records": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    lengths = [len(r.get("contents") or "") for r in rows]
    print(f"\n{len(rows):,} cases of {total:,}")
    for b, n in sorted(businesses.items(), key=lambda kv: -kv[1]):
        print(f"  {b:12s} {n:>6,}")
    if lengths:
        print(f"\n  contents: mean {sum(lengths) // len(lengths):,} chars, "
              f"max {max(lengths):,}")
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()

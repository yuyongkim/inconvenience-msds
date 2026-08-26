"""Build the paper 2 drug corpus, without knocking over the service it reads.

The two MFDS services describe the same product from different angles, so this
pairs them on the item sequence number: the approval register supplies the
ingredient and classification, e약은요 supplies the prose worth reading aloud.

Politeness is the design constraint, not an afterthought. These calls go through
the chemical information service that serves chemip.yule.pics, and an earlier
sweep at a third of a second between requests pushed it into 429s and slowed the
live site. So this waits longer between calls, backs off when it is told to,
and stops entirely rather than hammering through a sustained rate limit.

The register has no listing call, only substring search on the product name, so
the sweep walks dosage-form words that nearly every Korean product name carries.

Usage:
    python scripts/paper2_fetch_drugs.py [--target 1500] [--delay 1.5]
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "data" / "paper2" / "drug_corpus.json"

SERVICE = "http://127.0.0.1:7011/api/drugs"
PAGE = 50

TERMS = ["정", "캡슐", "시럽", "주", "액", "산", "과립", "크림", "연고", "점안"]

# Seconds to wait after a 429 before trying again, then again, then give up.
BACKOFF = (20, 60, 120)


def get(path: str, delay: float) -> dict | None:
    """One request, with the rate limit treated as an instruction rather than an error."""
    url = f"{SERVICE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "kosha-braille/paper2"})
    for wait in BACKOFF + (None,):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and wait is not None:
                print(f"    rate limited; waiting {wait}s", flush=True)
                time.sleep(wait)
                continue
            return None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            time.sleep(delay * 2)
            continue
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=1500,
                    help="stop once this many paired records are held")
    ap.add_argument("--delay", type=float, default=1.5,
                    help="seconds between requests; this shares a live service")
    args = ap.parse_args()

    paired: dict[str, dict] = {}
    if OUT.exists():
        try:
            prev = json.loads(OUT.read_text(encoding="utf-8"))
            paired = {r["item_seq"]: r for r in prev.get("records", [])}
            print(f"carrying forward {len(paired):,} records\n")
        except (json.JSONDecodeError, OSError):
            paired = {}

    calls = 0
    for term in TERMS:
        if len(paired) >= args.target:
            break
        page = 1
        while len(paired) < args.target:
            d = get(f"/search?q={urllib.parse.quote(term)}&page={page}&limit={PAGE}",
                    args.delay)
            calls += 1
            if not d:
                break
            appr = {i.get("ITEM_SEQ"): i for i in d.get("approval", {}).get("items", [])}
            easy = {i.get("itemSeq"): i for i in d.get("easyInfo", {}).get("items", [])}
            if not appr and not easy:
                break
            for seq in set(appr) | set(easy):
                if not seq or seq in paired:
                    continue
                paired[seq] = {"item_seq": seq,
                               "approval": appr.get(seq, {}),
                               "easy": easy.get(seq, {})}
            page += 1
            time.sleep(args.delay)
        print(f"  {term:6s} running total {len(paired):,} records, {calls} calls",
              flush=True)

    # Pairing pass. Searching both services with the same dosage-form word does
    # not line them up: each matches its own name field and pages independently,
    # so the first sweep produced 1,525 records and 17 pairs. Looking each
    # approval record up by its exact product name does line them up, because
    # the item sequence number comes back identical.
    unpaired = [r for r in paired.values() if r["approval"] and not r["easy"]]
    print(f"\npairing {len(unpaired):,} approval-only records by exact name",
          flush=True)
    filled = 0
    for i, rec in enumerate(unpaired, 1):
        name = (rec["approval"].get("ITEM_NAME") or "").strip()
        if not name:
            continue
        d = get(f"/easy?q={urllib.parse.quote(name)}&limit=5", args.delay)
        calls += 1
        if d:
            for item in d.get("items", []):
                if item.get("itemSeq") == rec["item_seq"]:
                    rec["easy"] = item
                    filled += 1
                    break
        if i % 50 == 0:
            print(f"    {i}/{len(unpaired)} looked up, {filled} paired", flush=True)
        time.sleep(args.delay)
    print(f"  paired {filled:,} more", flush=True)

    both = sum(1 for r in paired.values() if r["approval"] and r["easy"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": "MFDS DrugPrdtPrmsnInfoService07 + DrbEasyDrugInfoService, "
                  "paired on ITEM_SEQ, read through the chemip drug service",
        "search_terms": TERMS,
        "api_calls": calls,
        "records": sorted(paired.values(), key=lambda r: r["item_seq"]),
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n{len(paired):,} records over {calls} calls")
    print(f"  with both services: {both:,}")
    print(f"  approval only     : {sum(1 for r in paired.values() if r['approval'] and not r['easy']):,}")
    print(f"  e약은요 only        : {sum(1 for r in paired.values() if r['easy'] and not r['approval']):,}")
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()

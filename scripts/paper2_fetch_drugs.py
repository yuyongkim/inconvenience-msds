"""Build the paper 2 drug corpus from the two MFDS services.

The services describe the same product from different angles, so this pairs them
on the item sequence number: the approval register supplies the ingredient and
classification, e약은요 supplies the prose worth reading aloud.

An earlier version of this script went through the chemical information service
that serves chemip.yule.pics, on the theory that direct calls to data.go.kr were
being refused. They were not. The key in .env is stored quoted and split across
two lines, and a line-at-a-time parser handed the portal `"KEY` — which it
answers with SERVICE_KEY_IS_NOT_REGISTERED_ERROR, an error that names the key
and so reads as an authorisation problem. `scripts/keys.py` parses the file
properly and the portal answers normally. Nothing was ever wrong with the key,
and the detour also put load on a live service for no reason.

The register has no listing call, only substring search on the product name, so
the sweep walks dosage-form words that nearly every Korean product name carries.

Usage:
    python scripts/paper2_fetch_drugs.py [--target 1500] [--delay 0.4]
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
OUT = PROJECT_ROOT / "data" / "paper2" / "drug_corpus.json"

APPROVAL_URL = ("https://apis.data.go.kr/1471000/DrugPrdtPrmsnInfoService07/"
                "getDrugPrdtPrmsnInq07")
EASY_URL = ("https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/"
            "getDrbEasyDrugList")

PAGE = 100      # the portal's per-request ceiling

TERMS = ["정", "캡슐", "시럽", "주", "액", "산", "과립", "크림", "연고", "점안"]


def call(url: str, key: str, params: dict, attempts: int = 3) -> list[dict]:
    """One search, returning items. A portal-level refusal stops the run."""
    query = {"serviceKey": key, "type": "json", **params}
    for attempt in range(attempts):
        try:
            d = requests.get(url, params=query, timeout=120, verify=False).json()
            header = d.get("header") or d.get("body", {}).get("header") or {}
            code = header.get("resultCode")
            if code not in (None, "00"):
                raise SystemExit(f"{code}: {header.get('resultMsg')}")
            items = (d.get("body") or {}).get("items", [])
            if isinstance(items, dict):
                items = items.get("item", [])
            if isinstance(items, dict):
                items = [items]
            return [i for i in items if isinstance(i, dict)]
        except SystemExit:
            raise
        except Exception:
            if attempt < attempts - 1:
                time.sleep(2 ** attempt)
    return []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=1500,
                    help="stop once this many records are held")
    ap.add_argument("--delay", type=float, default=0.4)
    args = ap.parse_args()

    key = keys.service_key()

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
            appr = {i.get("ITEM_SEQ"): i for i in call(
                APPROVAL_URL, key, {"item_name": term, "pageNo": page, "numOfRows": PAGE})}
            easy = {i.get("itemSeq"): i for i in call(
                EASY_URL, key, {"itemName": term, "pageNo": page, "numOfRows": PAGE})}
            calls += 2
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

    # Pairing pass, and the direction matters. Looking an approval record up in
    # e약은요 fails almost always: the register carries every product ever
    # approved, including 1960s registrations, while e약은요 only carries what is
    # currently marketed. Going the other way succeeds, because anything with a
    # patient leaflet is necessarily an approved product. A first attempt ran it
    # the wrong way round and paired 0 of 685.
    unpaired = [r for r in paired.values() if r["easy"] and not r["approval"]]
    print(f"\npairing {len(unpaired):,} e약은요 records against the register",
          flush=True)
    filled = 0
    for i, rec in enumerate(unpaired, 1):
        name = (rec["easy"].get("itemName") or "").strip()
        if not name:
            continue
        calls += 1
        for item in call(APPROVAL_URL, key, {"item_name": name, "numOfRows": 5}):
            if item.get("ITEM_SEQ") == rec["item_seq"]:
                rec["approval"] = item
                filled += 1
                break
        if i % 100 == 0:
            print(f"    {i}/{len(unpaired)} looked up, {filled} paired", flush=True)
        time.sleep(args.delay)
    print(f"  paired {filled:,}", flush=True)

    both = sum(1 for r in paired.values() if r["approval"] and r["easy"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": "MFDS DrugPrdtPrmsnInfoService07 + DrbEasyDrugInfoService "
                  "(data.go.kr), paired on ITEM_SEQ",
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

"""Build the paper 2 drug corpus by walking both MFDS registers.

The two services describe the same product from different angles, so this pairs
them on the item sequence number: the approval register supplies the ingredient
and the classification, e약은요 supplies the prose worth reading aloud.

Two earlier premises turned out to be wrong, and both cost real time.

The first was that direct calls to data.go.kr were being refused, which led to
routing this through the chemical information service that already held the key.
They were not refused. The key in .env is stored quoted and split across two
lines, and a line-at-a-time parser handed the portal `"KEY` — which it answers
with SERVICE_KEY_IS_NOT_REGISTERED_ERROR, an error that names the key and so
reads as an authorisation problem. `scripts/keys.py` parses it properly.

The second was that the approval register offers no listing call, only substring
search on the product name, so the corpus was built by sweeping dosage-form
words. Both services page perfectly well with no filter at all: 4,762 leaflets
and 42,988 approved products, enumerated. The sweep had been returning whatever
its first search term matched and stopping at a target, which is a sample shaped
by the search term rather than by the register.

The leaflets are the smaller set and the more valuable one, because a patient
leaflet is what a reader is actually handed. So they are collected in full, and
the approval register is walked to fill in the ingredient and classification
that the leaflet does not carry.

Usage:
    python scripts/paper2_fetch_drugs.py [--approval-limit 0] [--delay 0.3]
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

# Codes that will not fix themselves: the key is wrong, expired, unregistered,
# or over its quota. Anything else — 01 APPLICATION_ERROR, 02 DB_ERROR, a
# timeout — is the portal having a moment, and retrying is the right answer.
# An earlier version stopped the whole run on any non-zero code, which threw
# away 2,510 collected records because the portal returned 01 once.
FATAL_CODES = {"20", "21", "22", "30", "31", "32", "33"}


def call(url: str, key: str, params: dict, attempts: int = 4) -> tuple[list[dict], int]:
    """One page. Returns its items and the register's total count."""
    query = {"serviceKey": key, "type": "json", **params}
    for attempt in range(attempts):
        try:
            d = requests.get(url, params=query, timeout=120, verify=False).json()
            header = d.get("header") or d.get("body", {}).get("header") or {}
            code = header.get("resultCode")
            if code in FATAL_CODES:
                raise SystemExit(f"{code}: {header.get('resultMsg')}")
            if code not in (None, "00"):
                raise RuntimeError(f"{code}: {header.get('resultMsg')}")
            body = d.get("body") or {}
            items = body.get("items", [])
            if isinstance(items, dict):
                items = items.get("item", [])
            if isinstance(items, dict):
                items = [items]
            return [i for i in items if isinstance(i, dict)], int(body.get("totalCount") or 0)
        except SystemExit:
            raise
        except Exception:
            if attempt < attempts - 1:
                time.sleep(2 ** attempt)
    return [], 0


def walk(url: str, key: str, label: str, delay: float, limit: int = 0):
    """Every page of a register, in order."""
    page = 1
    seen = 0
    while True:
        items, total = call(url, key, {"pageNo": page, "numOfRows": PAGE})
        if not items:
            break
        seen += len(items)
        yield items
        if page % 20 == 0 or seen >= total:
            print(f"  {label}: {seen:,}/{total:,}", flush=True)
        if len(items) < PAGE or seen >= total or (limit and seen >= limit):
            break
        page += 1
        time.sleep(delay)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--approval-limit", type=int, default=0,
                    help="0 walks the whole approval register")
    ap.add_argument("--delay", type=float, default=0.3)
    args = ap.parse_args()

    key = keys.service_key()

    print("e약은요 (patient leaflets)")
    easy: dict[str, dict] = {}
    for batch in walk(EASY_URL, key, "leaflets", args.delay):
        for it in batch:
            seq = it.get("itemSeq")
            if seq:
                easy[seq] = it

    print("\n허가등록부 (approved products)")
    approval: dict[str, dict] = {}
    for batch in walk(APPROVAL_URL, key, "products", args.delay,
                      limit=args.approval_limit):
        for it in batch:
            seq = it.get("ITEM_SEQ")
            if seq:
                approval[seq] = it

    # A leaflet is what a reader is handed, so the corpus is keyed on those and
    # the approval register fills in what the leaflet leaves out. Approved
    # products with no leaflet are kept too, but they are a different document —
    # a few short fields, not prose — and the manifest says how many there are
    # so the paper can report the two apart.
    records = []
    for seq, leaf in easy.items():
        records.append({"item_seq": seq, "easy": leaf,
                        "approval": approval.get(seq, {})})
    paired = sum(1 for r in records if r["approval"])
    for seq, appr in approval.items():
        if seq not in easy:
            records.append({"item_seq": seq, "easy": {}, "approval": appr})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": "MFDS DrugPrdtPrmsnInfoService07 + DrbEasyDrugInfoService "
                  "(data.go.kr), both registers enumerated, paired on ITEM_SEQ",
        "leaflets": len(easy),
        "approved_products": len(approval),
        "paired_both_services": paired,
        "note": "A record with a leaflet is patient-facing prose; one without is "
                "a handful of approval fields. They are different documents and "
                "the paper reports them apart.",
        "records": sorted(records, key=lambda r: r["item_seq"]),
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n{len(records):,} records")
    print(f"  leaflets            : {len(easy):,}")
    print(f"  approved products   : {len(approval):,}")
    print(f"  leaflet + approval  : {paired:,}")
    print(f"  approval only       : {len(records) - len(easy):,}")
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()

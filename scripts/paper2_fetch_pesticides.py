"""Build the paper 2 pesticide corpus from the MFDS register.

95,912 rows, and unlike the drug services this one pages properly: give it a
start and end index and it returns that slice. So the collection is a straight
walk rather than a sweep over search terms.

The rows are approved *uses*, not products — the same pesticide appears once per
crop-and-pest pairing — so a slice of a few thousand still covers a wide range
of products. The default target is a sample rather than the whole register,
because the paper needs a rate and a distribution, not a mirror of a government
database that changes weekly.

Usage:
    python scripts/paper2_fetch_pesticides.py [--target 3000] [--delay 0.6]
"""

from __future__ import annotations

import argparse
import io
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "data" / "paper2" / "pesticide_corpus.json"

SERVICE = "http://openapi.foodsafetykorea.go.kr/api"
SERVICE_ID = "I1910"
PAGE = 1000            # the portal's per-request ceiling


def load_key() -> str:
    """The portal key, read from .env and never printed."""
    env = {}
    for line in io.open(PROJECT_ROOT / ".env", encoding="utf-8-sig"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip().lower()] = v.strip()
    key = env.get("food")
    if not key:
        raise SystemExit("no `Food` key in .env")
    return key


def fetch(key: str, start: int, end: int, attempts: int = 3) -> tuple[list, int]:
    url = f"{SERVICE}/{key}/{SERVICE_ID}/json/{start}/{end}"
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                d = json.loads(r.read().decode("utf-8", "replace"))
            root = d.get(SERVICE_ID) or {}
            result = root.get("RESULT") or {}
            code = result.get("CODE")
            if code and code != "INFO-000":
                # A service-level refusal will not fix itself on retry.
                raise SystemExit(f"{code}: {result.get('MSG')}")
            total = int(root.get("total_count") or 0)
            return root.get("row") or [], total
        except SystemExit:
            raise
        except Exception:
            if attempt < attempts - 1:
                time.sleep(2 ** attempt)
    return [], 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=3000)
    ap.add_argument("--delay", type=float, default=0.6)
    args = ap.parse_args()

    key = load_key()
    rows: list[dict] = []
    total = 0
    start = 1
    while len(rows) < args.target:
        end = min(start + PAGE - 1, args.target)
        got, total = fetch(key, start, end)
        if not got:
            break
        rows.extend(got)
        print(f"  {len(rows):,}/{args.target:,} of {total:,} in the register", flush=True)
        if len(got) < (end - start + 1):
            break
        start = end + 1
        time.sleep(args.delay)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": "식품의약품안전처 농약 등록정보 (openapi.foodsafetykorea.go.kr, I1910)",
        "register_total": total,
        "collected": len(rows),
        "note": "Rows are approved uses, not products: one pesticide appears "
                "once per crop-and-pest pairing.",
        "records": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    products = len({r.get("PRDLST_KOR_NM") for r in rows if r.get("PRDLST_KOR_NM")})
    crops = len({r.get("CROPS_NM") for r in rows if r.get("CROPS_NM")})
    print(f"\n{len(rows):,} rows of {total:,}")
    print(f"  distinct products: {products:,}")
    print(f"  distinct crops   : {crops:,}")
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()

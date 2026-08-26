"""Paper-2 probe — MFDS e약은요 (DrbEasyDrugList) sanity check.

Reuses the data.go.kr key found in C:/Users/USER/Desktop/drugs/backend/.env.
Fetches a few sample drugs by Korean product name and pipes each result
through pipeline.ko_braille. Prints char count, braille cell count, and
head previews so we can confirm the encoder handles pharma text out of the box.
"""
import os
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

BRAILLE_ROOT = Path(r"C:\Users\USER\Desktop\Braille")
sys.path.insert(0, str(BRAILLE_ROOT))
from pipeline.ko_braille import encode_korean_braille

API_KEY = os.environ.get("DATA_GO_KR_SERVICE_KEY", "")
if not API_KEY:
    raise SystemExit(
        "DATA_GO_KR_SERVICE_KEY is not set. Request a service key at "
        "data.go.kr and set it in the environment before running this script."
    )
URL = "https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"

QUERIES = ["타이레놀", "아스피린", "게보린"]
FIELDS = [
    ("entpName", "제조사"),
    ("itemName", "제품명"),
    ("efcyQesitm", "효능"),
    ("useMethodQesitm", "용법"),
    ("atpnWarnQesitm", "경고"),
    ("atpnQesitm", "주의사항"),
    ("intrcQesitm", "상호작용"),
    ("seQesitm", "부작용"),
    ("depositMethodQesitm", "보관방법"),
]


def fetch(query: str):
    qs = urllib.parse.urlencode(
        {
            "serviceKey": API_KEY,
            "itemName": query,
            "numOfRows": "1",
            "pageNo": "1",
            "type": "json",
        }
    )
    with urllib.request.urlopen(f"{URL}?{qs}", timeout=15) as r:
        text = r.read().decode("utf-8", errors="replace")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        print(f"  ! JSON parse failed for '{query}'. Raw head:")
        print(text[:400])
        return None
    body = payload.get("body", {}) if isinstance(payload, dict) else {}
    items = body.get("items")
    if not items:
        return None
    if isinstance(items, dict):
        item = items.get("item")
        if isinstance(item, list):
            return item[0] if item else None
        return item
    if isinstance(items, list) and items:
        return items[0]
    return None


def build_text(item: dict) -> str:
    parts = []
    for key, label in FIELDS:
        v = item.get(key)
        if v and str(v).strip():
            parts.append(f"{label}: {str(v).strip()}")
    return "\n".join(parts)


def main():
    print("=" * 72)
    print("  MFDS e약은요 sanity probe")
    print("=" * 72)
    for q in QUERIES:
        print(f"\n[{q}]")
        try:
            item = fetch(q)
        except Exception as exc:
            print(f"  request failed: {exc}")
            continue
        if not item:
            print("  no result")
            continue
        text_ko = build_text(item)
        braille = encode_korean_braille(text_ko)
        print(f"  product : {item.get('itemName')}")
        print(f"  company : {item.get('entpName')}")
        print(f"  chars   : {len(text_ko)}")
        print(f"  cells   : {len(braille)}")
        print(f"  preview : {text_ko[:140].replace(chr(10), ' / ')}")
        print(f"  braille : {braille[:50]}")


if __name__ == "__main__":
    main()

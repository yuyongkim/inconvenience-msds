"""Paper-2 probe — MFDS 의약품 제품허가정보 (상세).

Tries the detailed drug product approval API. This API is far richer than
e약은요 (general public summary) — it carries 30+ fields including
효능효과 / 용법용량 / 사용상의주의사항 / 첨가제 / 보관방법 / 유효기간 /
임부 카테고리 / 어린이 / 노약자 / 운전·작업기계 등.

If the same data.go.kr key is approved for this API too, paper 2 has a
much deeper pharmaceutical domain right out of the gate.

Tries multiple endpoint versions because MFDS rolls these forward.
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
# MFDS rolls these forward; try newest first.
ENDPOINTS = [
    "http://apis.data.go.kr/1471000/DrugPrdtPrmsnInfoService06/getDrugPrdtPrmsnDtlInq05",
    "http://apis.data.go.kr/1471000/DrugPrdtPrmsnInfoService05/getDrugPrdtPrmsnDtlInq04",
    "http://apis.data.go.kr/1471000/DrugPrdtPrmsnInfoService04/getDrugPrdtPrmsnDtlInq03",
    "http://apis.data.go.kr/1471000/DrugPrdtPrmsnInfoService03/getDrugPrdtPrmsnDtlInq02",
    "http://apis.data.go.kr/1471000/DrugPrdtPrmsnInfoService/getDrugPrdtPrmsnDtlInq",
]

QUERY_ITEM = "타이레놀"


def try_endpoint(url: str):
    qs = urllib.parse.urlencode(
        {
            "serviceKey": API_KEY,
            "item_name": QUERY_ITEM,
            "numOfRows": "1",
            "pageNo": "1",
            "type": "json",
        }
    )
    req = urllib.request.Request(
        f"{url}?{qs}",
        headers={"User-Agent": "Mozilla/5.0 (KOSHA-Braille paper-2 probe)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
        status = 200
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:300]
    except Exception as e:
        return None, f"exception: {e}"
    text = raw.decode("utf-8", errors="replace")
    return status, text


def main():
    print("=" * 72)
    print("  MFDS 의약품 제품허가정보 (상세) sanity probe")
    print("=" * 72)
    for url in ENDPOINTS:
        version = url.split("DrugPrdtPrmsnInfoService", 1)[1].split("/")[0] or "(base)"
        print(f"\n[Service version: {version}]")
        print(f"  URL: {url}")
        status, body = try_endpoint(url)
        print(f"  status: {status}")
        if status == 200 and body:
            head = body[:600].replace("\n", " ")
            print(f"  head: {head}")
            try:
                payload = json.loads(body)
                # try to find an item
                resp = payload.get("body", {}) if isinstance(payload, dict) else {}
                if "items" in resp:
                    items = resp["items"]
                    item = None
                    if isinstance(items, list) and items:
                        item = items[0]
                    elif isinstance(items, dict):
                        it = items.get("item")
                        if isinstance(it, list) and it:
                            item = it[0]
                        elif isinstance(it, dict):
                            item = it
                    if item:
                        keys = list(item.keys())
                        print(f"  fields ({len(keys)}): {keys[:20]}")
                        # build a small text and braille it
                        text_ko_parts = []
                        for k in keys[:8]:
                            v = item.get(k)
                            if v and isinstance(v, str) and v.strip():
                                text_ko_parts.append(f"{k}: {v.strip()[:200]}")
                        if text_ko_parts:
                            text_ko = "\n".join(text_ko_parts)
                            braille = encode_korean_braille(text_ko)
                            print(f"  text chars : {len(text_ko)}")
                            print(f"  braille    : {len(braille)} cells")
                            print(f"  preview    : {text_ko[:200].replace(chr(10),' / ')}")
            except json.JSONDecodeError:
                print("  (response is not JSON — likely XML)")
        elif body:
            print(f"  body head: {body[:300]}")


if __name__ == "__main__":
    main()

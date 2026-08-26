"""Paper-2 probe — AirKorea 시도별 실시간 측정정보 (data.go.kr).

Endpoint:
  http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty

Returns the most recent PM10/PM2.5/O3/NO2/CO/SO2 readings per station in a
selected sido (시도). Re-uses the same MFDS_API_KEY (data.go.kr account key).

Output: a short Korean weather-bulletin-style summary per station, then
encoded to Korean braille. This is the prototype for the AirKorea case study
in Paper 2 (real-time public-safety stream).
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
URL = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"

SIDOS = ["서울", "부산", "전국"]

GRADE_KO = {
    "1": "좋음",
    "2": "보통",
    "3": "나쁨",
    "4": "매우 나쁨",
    "-": "정보없음",
    "": "정보없음",
}


def fetch(sido: str):
    qs = urllib.parse.urlencode(
        {
            "serviceKey": API_KEY,
            "sidoName": sido,
            "returnType": "json",
            "numOfRows": "3",
            "pageNo": "1",
            "ver": "1.3",
        }
    )
    req = urllib.request.Request(
        f"{URL}?{qs}",
        headers={"User-Agent": "Mozilla/5.0 (KOSHA-Braille paper-2 probe)"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read()
    text = raw.decode("utf-8", errors="replace")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        print(f"  ! JSON parse failed for sido='{sido}'. Raw head:")
        print(text[:400])
        return []
    response = payload.get("response", {}) if isinstance(payload, dict) else {}
    body = response.get("body", {}) if isinstance(response, dict) else {}
    items = body.get("items")
    if isinstance(items, list):
        return items
    if isinstance(items, dict):
        item = items.get("item")
        return item if isinstance(item, list) else ([item] if item else [])
    return []


def build_text(sido: str, item: dict) -> str:
    station = item.get("stationName") or "측정소"
    dt = item.get("dataTime") or ""
    pm10 = item.get("pm10Value") or "-"
    pm10_grade = GRADE_KO.get(item.get("pm10Grade") or "-", "정보없음")
    pm25 = item.get("pm25Value") or "-"
    pm25_grade = GRADE_KO.get(item.get("pm25Grade") or "-", "정보없음")
    o3 = item.get("o3Value") or "-"
    no2 = item.get("no2Value") or "-"
    co = item.get("coValue") or "-"
    so2 = item.get("so2Value") or "-"
    khai_grade = GRADE_KO.get(item.get("khaiGrade") or "-", "정보없음")

    return (
        f"{sido} {station} 대기질 정보 (기준 {dt})\n"
        f"통합대기환경지수: {khai_grade}\n"
        f"미세먼지(PM10): {pm10} 마이크로그램, {pm10_grade}\n"
        f"초미세먼지(PM2.5): {pm25} 마이크로그램, {pm25_grade}\n"
        f"오존: {o3} ppm\n"
        f"이산화질소: {no2} ppm\n"
        f"일산화탄소: {co} ppm\n"
        f"아황산가스: {so2} ppm"
    )


def main():
    print("=" * 72)
    print("  AirKorea 시도별 실시간 측정정보 sanity probe")
    print("=" * 72)
    for sido in SIDOS:
        print(f"\n[{sido}]")
        try:
            items = fetch(sido)
        except Exception as exc:
            print(f"  request failed: {exc}")
            continue
        if not items:
            print("  no items returned")
            continue
        for it in items[:2]:
            text_ko = build_text(sido, it)
            braille = encode_korean_braille(text_ko)
            print(f"  station : {it.get('stationName')}")
            print(f"  chars   : {len(text_ko)}")
            print(f"  cells   : {len(braille)}")
            print(f"  preview : {text_ko.replace(chr(10), ' / ')[:160]}")
            print(f"  braille : {braille[:50]}")
            print()


if __name__ == "__main__":
    main()

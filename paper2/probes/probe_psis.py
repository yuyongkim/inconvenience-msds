"""Paper-2 probe — PSIS 농약등록정보 (SVC01) sanity check.

Tries the same data.go.kr-issued key against PSIS. If the data.go.kr key is
not accepted by psis.rda.go.kr, prints the raw response so we can tell whether
a separate PSIS-portal key is required.

Endpoint:  http://psis.rda.go.kr/openApi/service.do
serviceCode SVC01 = 농약등록정보 목록 조회 (list search)
serviceType AA001 = XML
"""
import os
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
URL = "http://psis.rda.go.kr/openApi/service.do"

QUERIES = [
    {"label": "사과 작물", "params": {"cropName": "사과"}},
    {"label": "글리포세이트 성분", "params": {"pestiKorName": "글리포세이트"}},
    {"label": "라운드업 상표", "params": {"pestiBrandName": "라운드업"}},
]


def fetch(extra_params: dict) -> str:
    base = {
        "apiKey": API_KEY,
        "serviceCode": "SVC01",
        "serviceType": "AA001",
        "displayCount": "1",
        "startPoint": "1",
    }
    base.update(extra_params)
    qs = urllib.parse.urlencode(base)
    with urllib.request.urlopen(f"{URL}?{qs}", timeout=15) as r:
        raw = r.read()
    for enc in ("utf-8", "euc-kr", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def main():
    print("=" * 72)
    print("  PSIS 농약등록정보 sanity probe (using data.go.kr key)")
    print("=" * 72)
    for q in QUERIES:
        print(f"\n[{q['label']}]")
        try:
            text = fetch(q["params"])
        except Exception as exc:
            print(f"  request failed: {exc}")
            continue
        # peek at the response head so we can tell key-rejected vs got-data
        head = text[:600].replace("\n", " ")
        print(f"  response head: {head}")
        if "<resultCode>" in text or "<RESULT_CODE>" in text:
            # XML error envelope — usually carries SERVICE_KEY_IS_NOT_REGISTERED_ERROR etc.
            import re
            for tag in ("resultCode", "resultMsg", "RESULT_CODE", "RESULT_MSG", "errMsg"):
                m = re.search(fr"<{tag}>(.*?)</{tag}>", text)
                if m:
                    print(f"  {tag}: {m.group(1)}")


if __name__ == "__main__":
    main()

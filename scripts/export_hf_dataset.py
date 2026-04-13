"""
Export KOSHA-Braille dataset for HuggingFace Hub.

Generates:
  - data/hf_dataset/train.jsonl    (all 48,966 chemicals)
  - data/hf_dataset/README.md      (dataset card)

Each record:
  {
    "chem_id": "001008",
    "name_ko": "벤젠 (Benzene)",
    "cas_no": "71-43-2",
    "name_en": "Benzene",
    "sections": [
      {"section_no": 1, "title": "화학제품과 회사에 관한 정보", "text_ko": "...", "braille": "..."},
      ...
    ],
    "total_text_chars": 6123,
    "total_braille_chars": 11920
  }

Usage:
    python scripts/export_hf_dataset.py
    python scripts/export_hf_dataset.py --limit 100   # export first 100 only
"""

import json
import sqlite3
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from lxml import etree
from pipeline.ko_braille import encode_korean_braille

DB_PATH = "G:/MSDS/data/terminology.db"
OUTPUT_DIR = PROJECT_ROOT / "data" / "hf_dataset"

SECTION_TITLES = {
    1: '화학제품과 회사에 관한 정보',
    2: '유해성·위험성',
    3: '구성성분의 명칭 및 함유량',
    4: '응급조치 요령',
    5: '폭발·화재시 대처방법',
    6: '누출사고시 대처방법',
    7: '취급 및 저장방법',
    8: '노출방지 및 개인보호구',
    9: '물리화학적 특성',
    10: '안정성 및 반응성',
    11: '독성에 관한 정보',
    12: '환경에 미치는 영향',
    13: '폐기시 주의사항',
    14: '운송에 필요한 정보',
    15: '법적 규제현황',
    16: '그 밖의 참고사항',
}

GHS_PICTOGRAMS = {
    'GHS01': '폭발성', 'GHS02': '인화성', 'GHS03': '산화성',
    'GHS04': '고압가스', 'GHS05': '부식성', 'GHS06': '급성독성',
    'GHS07': '경고(피부자극/호흡기자극)', 'GHS08': '건강유해성(발암성/생식독성)',
    'GHS09': '수생환경유해성',
}


def _clean_msds_text(label: str, detail: str) -> str:
    import re
    if '그림문자' in label:
        parts = detail.split('|')
        meanings = []
        for part in parts:
            part = part.strip()
            m = re.match(r'(GHS\d{2})(?:\.gif)?', part)
            if m:
                meanings.append(GHS_PICTOGRAMS.get(m.group(1), m.group(1)))
            elif part:
                meanings.append(part)
        return ', '.join(meanings)
    detail = re.sub(r'(GHS\d{2})\.gif', lambda m: GHS_PICTOGRAMS.get(m.group(1), m.group(1)), detail)
    detail = detail.replace('|', ', ')
    return detail


def extract_section_text(xml_data: str) -> str:
    if not xml_data or xml_data == '<empty/>':
        return ''
    try:
        root = etree.fromstring(xml_data.encode('utf-8'))
        parts = []
        for item in root.findall('.//item'):
            label = item.findtext('msdsItemNameKor', '')
            detail = item.findtext('itemDetail', '')
            if detail and detail != '자료없음':
                cleaned = _clean_msds_text(label, detail)
                parts.append(f"{label}: {cleaned}" if label else cleaned)
        return '\n'.join(parts)
    except Exception:
        return ''


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=0, help='Limit chemicals (0=all)')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # Get all chemical IDs with MSDS
    chem_ids = [r[0] for r in conn.execute(
        "SELECT DISTINCT chem_id FROM msds_details ORDER BY chem_id"
    ).fetchall()]

    if args.limit > 0:
        chem_ids = chem_ids[:args.limit]

    # Get chemical metadata
    meta = {}
    for row in conn.execute("SELECT external_id, name, cas_no, name_en FROM chemical_terms WHERE external_id IS NOT NULL"):
        meta[row[0]] = {'name_ko': row[1], 'cas_no': row[2], 'name_en': row[3]}

    out_path = OUTPUT_DIR / "train.jsonl"
    t0 = time.time()
    count = 0
    total_text = 0
    total_braille = 0

    errors = []
    with open(out_path, 'w', encoding='utf-8') as f:
        for chem_id in chem_ids:
            info = meta.get(chem_id, {})
            sections = []
            chem_text = 0
            chem_braille = 0

            rows = conn.execute(
                "SELECT section_no, xml_data FROM msds_details WHERE chem_id = ? ORDER BY section_no",
                (chem_id,)
            ).fetchall()

            for sec_no, xml_data in rows:
                try:
                    text = extract_section_text(xml_data)
                    if text:
                        # Remove null bytes and surrogate characters
                        text = text.replace('\x00', '').encode('utf-8', errors='replace').decode('utf-8')
                        braille = encode_korean_braille(text)
                        sections.append({
                            'section_no': sec_no,
                            'title': SECTION_TITLES.get(sec_no, f'Section {sec_no}'),
                            'text_ko': text,
                            'braille': braille,
                        })
                        chem_text += len(text)
                        chem_braille += len(braille)
                except Exception as e:
                    errors.append(f"{chem_id}/sec{sec_no}: {e}")

            record = {
                'chem_id': chem_id,
                'name_ko': info.get('name_ko', ''),
                'cas_no': info.get('cas_no', ''),
                'name_en': info.get('name_en', ''),
                'sections': sections,
                'total_text_chars': chem_text,
                'total_braille_chars': chem_braille,
            }

            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            count += 1
            total_text += chem_text
            total_braille += chem_braille

            if count % 5000 == 0:
                elapsed = time.time() - t0
                rate = count / elapsed
                print(f"  {count:,}/{len(chem_ids):,}  ({rate:.1f}/s)")

    elapsed = time.time() - t0
    print(f"\nDone: {count:,} chemicals → {out_path}")
    print(f"  Total text:    {total_text:,} chars")
    print(f"  Total braille: {total_braille:,} chars")
    print(f"  Time: {elapsed:.1f}s ({count/elapsed:.1f} chemicals/s)")
    if errors:
        print(f"  Errors: {len(errors)}")
        for e in errors[:20]:
            print(f"    {e}")

    conn.close()


if __name__ == '__main__':
    main()

"""
Batch convert KOSHA MSDS → Korean Braille.

Reads 100 chemicals from the existing MSDS DB (G:/MSDS/data/terminology.db),
extracts safety text from all 16 sections, and converts to Korean braille.

No API calls needed — uses pre-fetched DB data.
"""

import csv
import json
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import etree
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.ko_braille import encode_korean_braille
from pipeline.encoder import encode_text_to_braille
from pipeline.decoder import braille_to_text
from pipeline.corrector import correct_noisy_text
from eval.similarity import normalized_edit_similarity

DB_PATH = "G:/MSDS/data/terminology.db"
OUTPUT_DIR = PROJECT_ROOT / "results" / "msds"


def get_chemicals(db_path: str, limit: int = 100) -> list[tuple[str, str]]:
    """Get (chem_id, name) pairs from DB."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT chem_id, xml_data FROM msds_details WHERE section_no=1 AND chem_id != 'null'")

    results = []
    for chem_id, xml_data in cur.fetchall():
        try:
            root = etree.fromstring(xml_data.encode('utf-8'))
            name = ''
            for item in root.findall('.//item'):
                if item.findtext('msdsItemCode', '') == 'A02':
                    name = item.findtext('itemDetail', '')
                    break
            if name and name != '자료없음':
                results.append((chem_id, name))
        except Exception:
            continue
        if len(results) >= limit:
            break

    conn.close()
    return results


def extract_msds_text(db_path: str, chem_id: str) -> dict:
    """Extract all MSDS sections as structured Korean text."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT section_no, xml_data FROM msds_details WHERE chem_id=? ORDER BY section_no",
                (chem_id,))

    sections = {}
    for sec_no, xml_data in cur.fetchall():
        try:
            root = etree.fromstring(xml_data.encode('utf-8'))
            items = root.findall('.//item')
            text_parts = []
            for item in items:
                label = item.findtext('msdsItemNameKor', '')
                detail = item.findtext('itemDetail', '')
                if detail and detail != '자료없음':
                    if label:
                        text_parts.append(f"{label}: {detail}")
                    else:
                        text_parts.append(detail)
            if text_parts:
                sections[sec_no] = '\n'.join(text_parts)
        except Exception:
            continue

    conn.close()
    return sections


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


def process_chemical(chem_id: str, name: str) -> dict:
    """Process one chemical: extract text, convert to braille."""
    sections = extract_msds_text(DB_PATH, chem_id)

    # Build full Korean MSDS text
    full_text_parts = [f"물질안전보건자료: {name}"]
    for sec_no in range(1, 17):
        if sec_no in sections:
            title = SECTION_TITLES.get(sec_no, f'섹션 {sec_no}')
            full_text_parts.append(f"\n{sec_no}. {title}")
            full_text_parts.append(sections[sec_no])

    ko_text = '\n'.join(full_text_parts)

    # Convert to Korean braille
    ko_braille = encode_korean_braille(ko_text)

    # Also create English version of key safety info (section 2: hazards)
    hazard_text = sections.get(2, '')
    section1_text = sections.get(1, '')

    return {
        'chem_id': chem_id,
        'name': name,
        'ko_text_chars': len(ko_text),
        'ko_braille_chars': len(ko_braille),
        'sections_available': len(sections),
        'ko_text_preview': ko_text[:200],
        'ko_braille_preview': ko_braille[:100],
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading chemicals from DB...")
    chemicals = get_chemicals(DB_PATH, limit=100)
    print(f"Selected {len(chemicals)} chemicals")

    results = []
    print(f"\nProcessing {len(chemicals)} chemicals...")

    # Process with thread pool (DB reads are I/O bound)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(process_chemical, cid, name): (cid, name)
            for cid, name in chemicals
        }
        for i, future in enumerate(as_completed(futures), 1):
            cid, name = futures[future]
            try:
                result = future.result()
                results.append(result)
                if i % 10 == 0 or i == len(chemicals):
                    print(f"  [{i:>3}/{len(chemicals)}] {name:<25} "
                          f"text={result['ko_text_chars']:>5} braille={result['ko_braille_chars']:>5}")
            except Exception as e:
                print(f"  [{i:>3}] ERROR {cid} {name}: {e}")

    # Save results
    csv_path = OUTPUT_DIR / "kosha_100_braille.csv"
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=[
            'chem_id', 'name', 'ko_text_chars', 'ko_braille_chars', 'sections_available'
        ])
        w.writeheader()
        for r in results:
            w.writerow({k: r[k] for k in w.fieldnames})

    # Save full braille output for sample
    json_path = OUTPUT_DIR / "kosha_100_samples.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results[:10], f, ensure_ascii=False, indent=2)

    # Summary
    total_text = sum(r['ko_text_chars'] for r in results)
    total_braille = sum(r['ko_braille_chars'] for r in results)
    avg_sections = sum(r['sections_available'] for r in results) / len(results)
    print(f"\n{'='*50}")
    print(f"  Processed: {len(results)} chemicals")
    print(f"  Total KR text: {total_text:,} chars")
    print(f"  Total KR braille: {total_braille:,} chars")
    print(f"  Avg sections/chem: {avg_sections:.1f}")
    print(f"  Saved: {csv_path}")


if __name__ == '__main__':
    main()

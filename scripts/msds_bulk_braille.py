"""
Bulk convert ALL complete KOSHA MSDS chemicals → Korean Braille.

Processes ~49K chemicals from terminology.db in streaming batches.
Outputs:
  - results/msds/bulk_stats.csv        (per-chemical stats)
  - results/msds/bulk_summary.json     (aggregate summary)
"""

import csv
import json
import logging
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import etree
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.ko_braille import encode_korean_braille

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / "results" / "msds" / "bulk_log.txt"),
    ],
)
log = logging.getLogger()

DB_PATH = "G:/MSDS/data/terminology.db"
OUTPUT_DIR = PROJECT_ROOT / "results" / "msds"

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


def get_all_complete_chemicals(db_path: str) -> list[tuple[str, str]]:
    """Get all chemicals with >=15 sections."""
    conn = sqlite3.connect(db_path)
    # Get chem_ids with enough sections
    chem_ids = [r[0] for r in conn.execute("""
        SELECT chem_id FROM msds_details
        GROUP BY chem_id HAVING COUNT(DISTINCT section_no) >= 15
    """).fetchall()]

    # Get names from section 1
    results = []
    for cid in chem_ids:
        row = conn.execute(
            "SELECT xml_data FROM msds_details WHERE chem_id=? AND section_no=1", (cid,)
        ).fetchone()
        if not row:
            continue
        try:
            root = etree.fromstring(row[0].encode('utf-8'))
            name = ''
            for item in root.findall('.//item'):
                if item.findtext('msdsItemCode', '') == 'A02':
                    name = item.findtext('itemDetail', '')
                    break
            if name and name != '자료없음':
                results.append((cid, name))
        except Exception:
            continue

    conn.close()
    return results


def extract_and_convert(db_path: str, chem_id: str, name: str) -> dict:
    """Extract MSDS text and convert to Korean braille for one chemical."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT section_no, xml_data FROM msds_details WHERE chem_id=? ORDER BY section_no",
        (chem_id,),
    ).fetchall()
    conn.close()

    sections = {}
    for sec_no, xml_data in rows:
        try:
            root = etree.fromstring(xml_data.encode('utf-8'))
            text_parts = []
            for item in root.findall('.//item'):
                label = item.findtext('msdsItemNameKor', '')
                detail = item.findtext('itemDetail', '')
                if detail and detail != '자료없음':
                    text_parts.append(f"{label}: {detail}" if label else detail)
            if text_parts:
                sections[sec_no] = '\n'.join(text_parts)
        except Exception:
            continue

    # Build full Korean MSDS text
    parts = [f"물질안전보건자료: {name}"]
    for sec_no in range(1, 17):
        if sec_no in sections:
            title = SECTION_TITLES.get(sec_no, f'섹션 {sec_no}')
            parts.append(f"\n{sec_no}. {title}")
            parts.append(sections[sec_no])
    ko_text = '\n'.join(parts)

    # Convert to Korean braille
    ko_braille = encode_korean_braille(ko_text)

    return {
        'chem_id': chem_id,
        'name': name,
        'ko_text_chars': len(ko_text),
        'ko_braille_chars': len(ko_braille),
        'sections_available': len(sections),
        'braille_ratio': round(len(ko_braille) / max(len(ko_text), 1), 3),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log.info("Loading all complete chemicals from DB...")
    chemicals = get_all_complete_chemicals(DB_PATH)
    log.info(f"Found {len(chemicals):,} chemicals to process")

    csv_path = OUTPUT_DIR / "bulk_stats.csv"
    fieldnames = ['chem_id', 'name', 'ko_text_chars', 'ko_braille_chars',
                  'sections_available', 'braille_ratio']

    total = len(chemicals)
    processed = 0
    errors = 0
    total_text = 0
    total_braille = 0
    start = time.time()

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Process in batches of 500 with thread pool
        batch_size = 500
        for batch_start in range(0, total, batch_size):
            batch = chemicals[batch_start:batch_start + batch_size]

            with ThreadPoolExecutor(max_workers=8) as ex:
                futures = {
                    ex.submit(extract_and_convert, DB_PATH, cid, name): (cid, name)
                    for cid, name in batch
                }
                for future in as_completed(futures):
                    cid, name = futures[future]
                    try:
                        result = future.result()
                        writer.writerow(result)
                        processed += 1
                        total_text += result['ko_text_chars']
                        total_braille += result['ko_braille_chars']
                    except Exception as e:
                        errors += 1
                        log.warning(f"Error {cid} {name}: {e}")

            elapsed = time.time() - start
            rate = processed / elapsed if elapsed > 0 else 0
            log.info(
                f"[{processed:>6,}/{total:,}] "
                f"text={total_text:>12,} braille={total_braille:>12,} "
                f"errors={errors} {rate:.1f}/s"
            )
            f.flush()

    elapsed = time.time() - start

    # Summary
    summary = {
        'total_chemicals': total,
        'processed': processed,
        'errors': errors,
        'total_ko_text_chars': total_text,
        'total_ko_braille_chars': total_braille,
        'avg_braille_ratio': round(total_braille / max(total_text, 1), 3),
        'elapsed_seconds': round(elapsed, 1),
        'rate_per_second': round(processed / max(elapsed, 1), 1),
    }

    summary_path = OUTPUT_DIR / "bulk_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    log.info(f"{'=' * 60}")
    log.info(f"  Processed: {processed:,} / {total:,} chemicals")
    log.info(f"  Errors: {errors}")
    log.info(f"  Total KR text: {total_text:,} chars")
    log.info(f"  Total KR braille: {total_braille:,} chars")
    log.info(f"  Avg braille/text ratio: {summary['avg_braille_ratio']}")
    log.info(f"  Time: {elapsed / 60:.1f} min ({summary['rate_per_second']}/s)")
    log.info(f"  Saved: {csv_path}")
    log.info(f"  Summary: {summary_path}")


if __name__ == '__main__':
    main()

"""
GHS H-statement / P-statement → Korean Braille lookup table.

Scans all chemicals in terminology.db section 2 (유해성·위험성),
extracts unique H-statements and P-statements with Korean text,
and converts each to Korean braille.

Outputs:
  - results/msds/ghs_h_statements.csv   (H-code, Korean text, Korean braille)
  - results/msds/ghs_p_statements.csv   (P-code, Korean text, Korean braille)
  - results/msds/ghs_summary.json       (stats)
"""

import csv
import json
import logging
import re
import sqlite3
import sys
import time
from collections import Counter
from lxml import etree
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.ko_braille import encode_korean_braille

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger()

DB_PATH = "G:/MSDS/data/terminology.db"
OUTPUT_DIR = PROJECT_ROOT / "results" / "msds"

# B0406 = 유해·위험문구 (H-statements)
# B040802 = 예방 (P-prevention), B040804 = 대응 (P-response)
# B040806 = 저장 (P-storage), B040808 = 폐기 (P-disposal)
H_ITEM_CODE = 'B0406'
P_ITEM_CODES = {'B040802', 'B040804', 'B040806', 'B040808'}

# Pattern: "H225 : 고인화성 액체 및 증기" or "P201 : 사용 전..."
STMT_PATTERN = re.compile(r'([HP]\d{3}(?:\+[HP]\d{3})*)\s*:\s*(.+)')


def extract_statements(xml_data: str) -> tuple[dict[str, str], dict[str, str]]:
    """Extract H and P statements from section 2 XML.
    Returns (h_dict, p_dict) mapping code → Korean text.
    """
    h_stmts = {}
    p_stmts = {}
    try:
        root = etree.fromstring(xml_data.encode('utf-8'))
    except Exception:
        return h_stmts, p_stmts

    for item in root.findall('.//item'):
        code = item.findtext('msdsItemCode', '')
        detail = item.findtext('itemDetail', '')
        if not detail or detail == '자료없음':
            continue

        target = None
        if code == H_ITEM_CODE:
            target = h_stmts
        elif code in P_ITEM_CODES:
            target = p_stmts
        else:
            continue

        for part in detail.split('|'):
            m = STMT_PATTERN.match(part.strip())
            if m:
                stmt_code = m.group(1)
                stmt_text = m.group(2).strip()
                # Keep the longest version (some chemicals have more detailed text)
                if stmt_code not in target or len(stmt_text) > len(target[stmt_code]):
                    target[stmt_code] = stmt_text

    return h_stmts, p_stmts


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    log.info("Loading section 2 data for all chemicals...")
    rows = conn.execute(
        "SELECT chem_id, xml_data FROM msds_details WHERE section_no=2"
    ).fetchall()
    conn.close()
    log.info(f"Loaded {len(rows):,} section 2 records")

    # Collect all unique statements
    all_h: dict[str, str] = {}
    all_p: dict[str, str] = {}
    h_freq: Counter = Counter()
    p_freq: Counter = Counter()
    chemicals_with_h = 0

    for cid, xml_data in rows:
        h_stmts, p_stmts = extract_statements(xml_data)
        if h_stmts:
            chemicals_with_h += 1
        for code, text in h_stmts.items():
            h_freq[code] += 1
            if code not in all_h or len(text) > len(all_h[code]):
                all_h[code] = text
        for code, text in p_stmts.items():
            p_freq[code] += 1
            if code not in all_p or len(text) > len(all_p[code]):
                all_p[code] = text

    log.info(f"Unique H-statements: {len(all_h)}")
    log.info(f"Unique P-statements: {len(all_p)}")
    log.info(f"Chemicals with H-statements: {chemicals_with_h:,}")

    # Convert to braille and write CSVs
    def write_statements(stmts: dict, freq: Counter, path: Path, label: str):
        rows_out = []
        for code in sorted(stmts.keys()):
            ko_text = stmts[code]
            full_text = f"{code} : {ko_text}"
            ko_braille = encode_korean_braille(full_text)
            rows_out.append({
                'code': code,
                'ko_text': ko_text,
                'ko_braille': ko_braille,
                'braille_chars': len(ko_braille),
                'frequency': freq[code],
            })

        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['code', 'ko_text', 'ko_braille',
                                                    'braille_chars', 'frequency'])
            writer.writeheader()
            writer.writerows(rows_out)

        log.info(f"  {label}: {len(rows_out)} statements → {path.name}")
        return rows_out

    h_rows = write_statements(all_h, h_freq, OUTPUT_DIR / "ghs_h_statements.csv", "H")
    p_rows = write_statements(all_p, p_freq, OUTPUT_DIR / "ghs_p_statements.csv", "P")

    # Summary
    summary = {
        'total_chemicals_scanned': len(rows),
        'chemicals_with_h_statements': chemicals_with_h,
        'unique_h_codes': len(all_h),
        'unique_p_codes': len(all_p),
        'top_10_h': h_freq.most_common(10),
        'top_10_p': p_freq.most_common(10),
        'h_braille_total_chars': sum(r['braille_chars'] for r in h_rows),
        'p_braille_total_chars': sum(r['braille_chars'] for r in p_rows),
    }

    summary_path = OUTPUT_DIR / "ghs_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    log.info(f"\nSummary saved: {summary_path}")
    log.info(f"Top H-codes: {', '.join(f'{c}({n})' for c, n in h_freq.most_common(5))}")
    log.info(f"Top P-codes: {', '.join(f'{c}({n})' for c, n in p_freq.most_common(5))}")


if __name__ == '__main__':
    main()

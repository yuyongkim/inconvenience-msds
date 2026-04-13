"""
Validate Korean MSDS → Korean Braille direct conversion quality.

Tests:
  1. Roundtrip: KR text → KR braille → KR text (encode-decode fidelity)
  2. Rule violations: check braille output for common errors
  3. Coverage: what fraction of input characters are successfully encoded

Runs on a random sample of chemicals from the DB.

Outputs:
  - results/msds/kr_braille_validation.csv   (per-chemical metrics)
  - results/msds/kr_braille_validation.json  (aggregate summary)
"""

import csv
import json
import logging
import random
import re
import sqlite3
import sys
import time
from lxml import etree
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.ko_braille import encode_korean_braille
from pipeline.ko_braille_decoder import decode_korean_braille
from eval.similarity import normalized_edit_similarity, chrf_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
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


def get_sample_chemicals(db_path: str, n: int = 500) -> list[tuple[str, str]]:
    """Get random sample of chemicals with complete sections."""
    conn = sqlite3.connect(db_path)
    chem_ids = [r[0] for r in conn.execute("""
        SELECT chem_id FROM msds_details
        GROUP BY chem_id HAVING COUNT(DISTINCT section_no) >= 15
    """).fetchall()]

    random.seed(42)
    sample_ids = random.sample(chem_ids, min(n, len(chem_ids)))

    results = []
    for cid in sample_ids:
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


def build_msds_text(db_path: str, chem_id: str, name: str) -> str:
    """Build full Korean MSDS text from DB."""
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

    parts = [f"물질안전보건자료: {name}"]
    for sec_no in range(1, 17):
        if sec_no in sections:
            title = SECTION_TITLES.get(sec_no, f'섹션 {sec_no}')
            parts.append(f"\n{sec_no}. {title}")
            parts.append(sections[sec_no])
    return '\n'.join(parts)


def count_rule_violations(braille: str) -> dict:
    """Check for common Korean braille rule violations."""
    violations = {}

    # 1. Empty cells in sequence (double blank = suspicious)
    double_blank = braille.count('\u2800\u2800')
    if double_blank > 0:
        violations['double_blank'] = double_blank

    # 2. Number indicator not followed by digit cell
    num_ind = '\u283C'  # ⠼ = 3-4-5-6
    for i, ch in enumerate(braille):
        if ch == num_ind and i + 1 < len(braille):
            next_ch = braille[i + 1]
            # Valid digit cells: ⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚
            valid_digits = set('\u2801\u2803\u2809\u2819\u2811\u280B\u281B\u2813\u280A\u281A')
            if next_ch not in valid_digits:
                violations['num_indicator_orphan'] = violations.get('num_indicator_orphan', 0) + 1

    # 3. Passthrough characters (not braille, not whitespace/newline)
    passthrough = 0
    for ch in braille:
        if ch not in ('\n', ' ', '\u2800') and not (0x2800 <= ord(ch) <= 0x28FF):
            passthrough += 1
    if passthrough > 0:
        violations['passthrough_chars'] = passthrough

    return violations


def analyze_coverage(original: str, braille: str) -> dict:
    """Analyze what fraction of input was successfully encoded."""
    total_chars = len(original)
    hangul_chars = sum(1 for ch in original if 0xAC00 <= ord(ch) <= 0xD7A3)
    digit_chars = sum(1 for ch in original if ch.isdigit())
    latin_chars = sum(1 for ch in original if ch.isascii() and ch.isalpha())
    space_chars = sum(1 for ch in original if ch in ' \n')
    other_chars = total_chars - hangul_chars - digit_chars - latin_chars - space_chars

    # Braille cells (non-space, non-newline)
    braille_cells = sum(1 for ch in braille if 0x2800 < ord(ch) <= 0x28FF)
    passthrough = sum(1 for ch in braille if ch not in ('\n', ' ', '\u2800') and not (0x2800 <= ord(ch) <= 0x28FF))

    return {
        'total_chars': total_chars,
        'hangul_chars': hangul_chars,
        'digit_chars': digit_chars,
        'latin_chars': latin_chars,
        'other_chars': other_chars,
        'braille_cells': braille_cells,
        'passthrough_chars': passthrough,
        'coverage_pct': round(100 * (1 - passthrough / max(total_chars, 1)), 2),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log.info("Sampling chemicals for validation...")
    chemicals = get_sample_chemicals(DB_PATH, n=500)
    log.info(f"Validating {len(chemicals)} chemicals")

    csv_path = OUTPUT_DIR / "kr_braille_validation.csv"
    fieldnames = [
        'chem_id', 'name', 'ko_text_chars', 'ko_braille_chars',
        'roundtrip_edit_sim', 'roundtrip_chrf',
        'violations', 'violation_count',
        'coverage_pct', 'passthrough_chars',
    ]

    results = []
    start = time.time()

    for i, (cid, name) in enumerate(chemicals, 1):
        try:
            ko_text = build_msds_text(DB_PATH, cid, name)
            ko_braille = encode_korean_braille(ko_text)
            decoded = decode_korean_braille(ko_braille)

            # Roundtrip metrics
            # Use ChrF (fast, O(n)) instead of edit distance (O(n²)) for long texts
            # For short texts (<2000 chars), also compute edit similarity
            chrf = chrf_score(ko_text, decoded)
            if len(ko_text) < 2000:
                edit_sim = normalized_edit_similarity(ko_text, decoded)
            else:
                # Sample-based: compare first+last 500 chars
                head_sim = normalized_edit_similarity(ko_text[:500], decoded[:500])
                tail_sim = normalized_edit_similarity(ko_text[-500:], decoded[-500:])
                edit_sim = (head_sim + tail_sim) / 2

            # Rule violations
            violations = count_rule_violations(ko_braille)
            violation_total = sum(violations.values())

            # Coverage
            coverage = analyze_coverage(ko_text, ko_braille)

            row = {
                'chem_id': cid,
                'name': name,
                'ko_text_chars': len(ko_text),
                'ko_braille_chars': len(ko_braille),
                'roundtrip_edit_sim': round(edit_sim, 4),
                'roundtrip_chrf': round(chrf, 4),
                'violations': json.dumps(violations, ensure_ascii=False) if violations else '',
                'violation_count': violation_total,
                'coverage_pct': coverage['coverage_pct'],
                'passthrough_chars': coverage['passthrough_chars'],
            }
            results.append(row)

            if i % 50 == 0 or i == len(chemicals):
                elapsed = time.time() - start
                avg_sim = sum(r['roundtrip_edit_sim'] for r in results) / len(results)
                avg_cov = sum(r['coverage_pct'] for r in results) / len(results)
                log.info(
                    f"[{i:>3}/{len(chemicals)}] "
                    f"avg_roundtrip={avg_sim:.4f} avg_coverage={avg_cov:.1f}% "
                    f"({elapsed:.0f}s)"
                )
        except Exception as e:
            log.warning(f"Error {cid} {name}: {e}")

    # Write CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Aggregate summary
    n = len(results)
    avg_edit = sum(r['roundtrip_edit_sim'] for r in results) / n
    avg_chrf = sum(r['roundtrip_chrf'] for r in results) / n
    avg_coverage = sum(r['coverage_pct'] for r in results) / n
    perfect = sum(1 for r in results if r['roundtrip_edit_sim'] >= 0.999)
    high = sum(1 for r in results if r['roundtrip_edit_sim'] >= 0.95)
    low = sum(1 for r in results if r['roundtrip_edit_sim'] < 0.80)
    total_violations = sum(r['violation_count'] for r in results)
    total_cells = sum(r['ko_braille_chars'] for r in results)

    summary = {
        'sample_size': n,
        'roundtrip': {
            'mean_edit_similarity': round(avg_edit, 4),
            'mean_chrf': round(avg_chrf, 4),
            'perfect_count': perfect,
            'high_count_95pct': high,
            'low_count_80pct': low,
        },
        'coverage': {
            'mean_pct': round(avg_coverage, 2),
        },
        'violations': {
            'total': total_violations,
            'per_1000_cells': round(1000 * total_violations / max(total_cells, 1), 2),
        },
        'total_ko_text_chars': sum(r['ko_text_chars'] for r in results),
        'total_ko_braille_chars': total_cells,
    }

    summary_path = OUTPUT_DIR / "kr_braille_validation.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start
    log.info(f"\n{'=' * 60}")
    log.info(f"  Sample: {n} chemicals")
    log.info(f"  Roundtrip edit similarity: {avg_edit:.4f}")
    log.info(f"  Roundtrip ChrF: {avg_chrf:.4f}")
    log.info(f"  Perfect roundtrip (>=99.9%): {perfect}/{n}")
    log.info(f"  High quality (>=95%): {high}/{n}")
    log.info(f"  Coverage: {avg_coverage:.1f}%")
    log.info(f"  Violations per 1000 cells: {summary['violations']['per_1000_cells']}")
    log.info(f"  Time: {elapsed:.0f}s")
    log.info(f"  Saved: {csv_path}")
    log.info(f"  Summary: {summary_path}")


if __name__ == '__main__':
    main()

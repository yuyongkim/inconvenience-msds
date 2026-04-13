"""
International Chemical Expansion via CAS Number Cross-referencing.

Links KOSHA Korean MSDS data with:
  - PubChem English safety data (56K records in msds_english)
  - EPA regulatory data (8K records in intl_regulatory)
  - KISCHEM first-aid data (7K records)
  - K-REACH registration (47K records)

Generates a bilingual (Korean + English) braille-ready dataset.

Usage:
    python scripts/intl_expansion.py --report     # Summary report
    python scripts/intl_expansion.py --export     # Export bilingual dataset
    python scripts/intl_expansion.py --export --limit 100
"""

import json
import sqlite3
import sys
import time
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = "G:/MSDS/data/terminology.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def generate_report():
    """Generate coverage report for international expansion."""
    conn = get_db()

    print("=" * 70)
    print("  International Chemical Expansion Report")
    print("=" * 70)

    # 1. KOSHA base
    kosha_total = conn.execute("SELECT count(DISTINCT chem_id) FROM msds_details").fetchone()[0]
    print(f"\n1. KOSHA Korean MSDS base: {kosha_total:,} chemicals")

    # 2. CAS coverage
    cas_total = conn.execute(
        "SELECT count(DISTINCT cas_no) FROM chemical_terms WHERE cas_no IS NOT NULL AND cas_no != ''"
    ).fetchone()[0]
    print(f"2. Unique CAS numbers: {cas_total:,}")

    # 3. English safety data
    en_total = conn.execute("SELECT count(*) FROM msds_english").fetchone()[0]
    en_with_ghs = conn.execute(
        "SELECT count(*) FROM msds_english WHERE ghs_classification IS NOT NULL AND ghs_classification != ''"
    ).fetchone()[0]
    en_with_hazard = conn.execute(
        "SELECT count(*) FROM msds_english WHERE hazard_statements IS NOT NULL AND hazard_statements != ''"
    ).fetchone()[0]
    print(f"3. English safety records: {en_total:,}")
    print(f"   - With GHS classification: {en_with_ghs:,}")
    print(f"   - With hazard statements: {en_with_hazard:,}")

    # 4. International regulatory
    intl_total = conn.execute("SELECT count(*) FROM intl_regulatory").fetchone()[0]
    intl_regs = conn.execute(
        "SELECT regulation, count(*) as n FROM intl_regulatory GROUP BY regulation ORDER BY n DESC"
    ).fetchall()
    print(f"4. International regulatory records: {intl_total:,}")
    for r in intl_regs[:5]:
        print(f"   - {r['regulation']}: {r['n']:,}")

    # 5. KISCHEM first-aid
    kischem_total = conn.execute("SELECT count(*) FROM kischem_safety").fetchone()[0]
    print(f"5. KISCHEM first-aid records: {kischem_total:,}")

    # 6. K-REACH
    kreach_total = conn.execute("SELECT count(*) FROM kreach_chemicals").fetchone()[0]
    print(f"6. K-REACH registered chemicals: {kreach_total:,}")

    # 7. Cross-reference coverage
    bilingual = conn.execute("""
        SELECT count(DISTINCT ct.cas_no)
        FROM chemical_terms ct
        JOIN msds_details md ON ct.external_id = md.chem_id
        JOIN msds_english me ON ct.external_id = me.chem_id
        WHERE ct.cas_no IS NOT NULL AND ct.cas_no != ''
    """).fetchone()[0]
    print(f"\n7. Bilingual coverage (KR MSDS + EN safety): {bilingual:,} chemicals")
    print(f"   = {bilingual/kosha_total*100:.1f}% of KOSHA base")

    # 8. Expansion potential
    en_only = conn.execute("""
        SELECT count(DISTINCT me.cas_no)
        FROM msds_english me
        LEFT JOIN chemical_terms ct ON me.cas_no = ct.cas_no
        WHERE ct.cas_no IS NULL
    """).fetchone()[0]
    print(f"\n8. Expansion potential:")
    print(f"   - EN-only chemicals (not in KOSHA): ~{en_only:,}")
    print(f"   - Total addressable: {kosha_total + en_only:,}")

    conn.close()

    print(f"\n{'=' * 70}")
    print(f"  Summary: {bilingual:,} chemicals with full bilingual braille coverage")
    print(f"  Korean MSDS (16 sections) + English GHS safety data")
    print(f"{'=' * 70}")


def export_bilingual(limit: int = 0):
    """Export bilingual braille-ready dataset."""
    from lxml import etree
    from pipeline.ko_braille import encode_korean_braille

    conn = get_db()
    output_dir = PROJECT_ROOT / "data" / "hf_dataset"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get chemicals with both KR MSDS and EN safety data
    rows = conn.execute("""
        SELECT ct.external_id as chem_id, ct.name as name_ko, ct.cas_no, ct.name_en,
               me.signal_word, me.ghs_classification, me.hazard_statements,
               me.precautionary_statements, me.pictograms
        FROM chemical_terms ct
        JOIN msds_english me ON ct.external_id = me.chem_id
        WHERE ct.cas_no IS NOT NULL AND ct.cas_no != ''
        AND ct.external_id IN (SELECT DISTINCT chem_id FROM msds_details)
        ORDER BY ct.external_id
    """).fetchall()

    if limit > 0:
        rows = rows[:limit]

    out_path = output_dir / "bilingual.jsonl"
    t0 = time.time()
    count = 0

    with open(out_path, 'w', encoding='utf-8') as f:
        for row in rows:
            # English safety info
            en_safety = {
                'signal_word': row['signal_word'] or '',
                'ghs_classification': row['ghs_classification'] or '',
                'hazard_statements': row['hazard_statements'] or '',
                'precautionary_statements': row['precautionary_statements'] or '',
                'pictograms': row['pictograms'] or '',
            }

            # Build summary text for braille
            en_text_parts = [f"Chemical: {row['name_en'] or row['name_ko']}"]
            if en_safety['signal_word']:
                en_text_parts.append(f"Signal Word: {en_safety['signal_word']}")
            if en_safety['hazard_statements']:
                en_text_parts.append(f"Hazard: {en_safety['hazard_statements'][:500]}")
            if en_safety['precautionary_statements']:
                en_text_parts.append(f"Precaution: {en_safety['precautionary_statements'][:500]}")

            en_summary = '\n'.join(en_text_parts)

            record = {
                'chem_id': row['chem_id'],
                'name_ko': row['name_ko'],
                'cas_no': row['cas_no'],
                'name_en': row['name_en'],
                'en_safety': en_safety,
                'en_summary_braille': encode_korean_braille(en_summary),
            }

            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            count += 1

            if count % 1000 == 0:
                elapsed = time.time() - t0
                print(f"  {count:,}/{len(rows):,}  ({count/elapsed:.1f}/s)")

    elapsed = time.time() - t0
    print(f"\nExported: {count:,} bilingual records → {out_path}")
    print(f"Time: {elapsed:.1f}s")

    conn.close()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', action='store_true', help='Print coverage report')
    parser.add_argument('--export', action='store_true', help='Export bilingual dataset')
    parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args()

    if args.report or not args.export:
        generate_report()

    if args.export:
        export_bilingual(args.limit)


if __name__ == '__main__':
    main()

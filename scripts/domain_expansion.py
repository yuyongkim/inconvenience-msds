"""
Domain Expansion: Beyond MSDS.

Converts additional safety/health documents to Korean braille:
  1. KISCHEM first-aid data (7,189 chemicals) → 응급처치 점자
  2. FDA drug labels (48,619 records via OpenFDA) → 의약품 라벨 점자
  3. Food allergen warnings (template-based) → 식품 알레르기 점자

Usage:
    python scripts/domain_expansion.py --kischem          # Export first-aid braille
    python scripts/domain_expansion.py --drugs --limit 100  # Export drug label braille
    python scripts/domain_expansion.py --food             # Export food allergen braille
    python scripts/domain_expansion.py --all --report     # Full report + export all
"""

import json
import sqlite3
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.ko_braille import encode_korean_braille

DB_PATH = "G:/MSDS/data/terminology.db"
OUTPUT_DIR = PROJECT_ROOT / "data" / "domain_expansion"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# 1. KISCHEM First-Aid → Braille
# ============================================================

def export_kischem_braille(limit: int = 0):
    """Export KISCHEM first-aid data as Korean braille."""
    conn = get_db()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = conn.execute(
        "SELECT * FROM kischem_safety ORDER BY data_no"
    ).fetchall()

    if limit > 0:
        rows = rows[:limit]

    out_path = OUTPUT_DIR / "kischem_firstaid_braille.jsonl"
    count = 0
    t0 = time.time()

    FIELD_LABELS = {
        'symptom': '증상',
        'inhale': '흡입시',
        'skin': '피부접촉시',
        'eyeball': '안구접촉시',
        'oral': '경구시',
        'etc': '기타',
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        for row in rows:
            # Build Korean text
            parts = [f"응급처치 정보: {row['chem_ko'] or row['chem_en']}"]
            if row['cas_no']:
                parts.append(f"CAS 번호: {row['cas_no']}")

            for field, label in FIELD_LABELS.items():
                val = row[field]
                if val and val.strip() and val.strip() != '·자료없음':
                    parts.append(f"\n{label}:")
                    parts.append(val.strip())

            text_ko = '\n'.join(parts)
            braille = encode_korean_braille(text_ko)

            record = {
                'data_no': row['data_no'],
                'chem_en': row['chem_en'],
                'chem_ko': row['chem_ko'],
                'cas_no': row['cas_no'],
                'text_ko': text_ko,
                'braille': braille,
                'text_chars': len(text_ko),
                'braille_cells': len(braille),
            }

            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            count += 1

    elapsed = time.time() - t0
    print(f"KISCHEM first-aid: {count:,} chemicals → {out_path}")
    print(f"  Time: {elapsed:.1f}s")
    conn.close()
    return count


# ============================================================
# 2. FDA Drug Labels → Braille
# ============================================================

def export_drug_braille(limit: int = 0):
    """Export FDA drug label data as Korean braille (key fields)."""
    conn = get_db()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = conn.execute(
        "SELECT chem_id, source, item_key, data FROM drug_mappings WHERE source = 'openfda' ORDER BY chem_id"
    ).fetchall()

    if limit > 0:
        rows = rows[:limit]

    out_path = OUTPUT_DIR / "drug_labels_braille.jsonl"
    count = 0
    t0 = time.time()

    # Key fields to extract from OpenFDA JSON
    KEY_FIELDS = [
        ('indications_and_usage', '적응증 및 용법'),
        ('warnings', '경고'),
        ('dosage_and_administration', '용량 및 투여'),
        ('active_ingredient', '활성 성분'),
        ('keep_out_of_reach_of_children', '어린이 주의사항'),
        ('pregnancy_or_breast_feeding', '임산부/수유부 주의'),
    ]

    with open(out_path, 'w', encoding='utf-8') as f:
        for row in rows:
            try:
                data = json.loads(row['data'])
            except (json.JSONDecodeError, TypeError):
                continue

            openfda = data.get('openfda', {})
            brand = (openfda.get('brand_name', [''])[0] if openfda.get('brand_name') else '')
            generic = (openfda.get('generic_name', [''])[0] if openfda.get('generic_name') else '')

            # Build text from key fields
            parts = [f"의약품 정보: {brand or generic or 'Unknown'}"]

            for field, label in KEY_FIELDS:
                val = data.get(field)
                if val:
                    text = val[0] if isinstance(val, list) else str(val)
                    text = text.strip()[:1000]  # Limit field length
                    if text:
                        parts.append(f"\n{label}:")
                        parts.append(text)

            text_ko = '\n'.join(parts)
            braille = encode_korean_braille(text_ko)

            record = {
                'chem_id': row['chem_id'],
                'brand_name': brand,
                'generic_name': generic,
                'text': text_ko,
                'braille': braille,
                'text_chars': len(text_ko),
                'braille_cells': len(braille),
            }

            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            count += 1

            if count % 5000 == 0:
                elapsed = time.time() - t0
                print(f"  {count:,}/{len(rows):,}")

    elapsed = time.time() - t0
    print(f"Drug labels: {count:,} records → {out_path}")
    print(f"  Time: {elapsed:.1f}s")
    conn.close()
    return count


# ============================================================
# 3. Food Allergen Warnings → Braille
# ============================================================

# Korea's Food Labeling Standards mandate disclosure of 22 allergens
KOREAN_ALLERGENS = {
    '알류(가금류)': 'Eggs (poultry)',
    '우유': 'Milk',
    '메밀': 'Buckwheat',
    '땅콩': 'Peanuts',
    '대두': 'Soybeans',
    '밀': 'Wheat',
    '고등어': 'Mackerel',
    '게': 'Crab',
    '새우': 'Shrimp',
    '돼지고기': 'Pork',
    '복숭아': 'Peach',
    '토마토': 'Tomato',
    '아황산류': 'Sulfites',
    '호두': 'Walnut',
    '닭고기': 'Chicken',
    '쇠고기': 'Beef',
    '오징어': 'Squid',
    '조개류': 'Shellfish',
    '잣': 'Pine nuts',
}


def export_food_allergen_braille():
    """Export Korean food allergen warnings as braille."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "food_allergens_braille.jsonl"

    count = 0
    with open(out_path, 'w', encoding='utf-8') as f:
        for allergen_ko, allergen_en in KOREAN_ALLERGENS.items():
            # Standard warning text per Korean Food Labeling Standards
            warning_text = f"알레르기 유발 성분: 이 제품은 {allergen_ko}을(를) 포함하고 있습니다."
            contains_text = f"원재료명: {allergen_ko} ({allergen_en}) 함유"

            full_text = f"{warning_text}\n{contains_text}"
            braille = encode_korean_braille(full_text)

            record = {
                'allergen_ko': allergen_ko,
                'allergen_en': allergen_en,
                'warning_text': full_text,
                'braille': braille,
                'braille_cells': len(braille),
            }

            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            count += 1

    print(f"Food allergens: {count} allergen warnings → {out_path}")
    return count


# ============================================================
# Report
# ============================================================

def print_report():
    conn = get_db()
    print("=" * 70)
    print("  Domain Expansion Report")
    print("=" * 70)

    kischem = conn.execute("SELECT count(*) FROM kischem_safety").fetchone()[0]
    drugs = conn.execute("SELECT count(*) FROM drug_mappings WHERE source='openfda'").fetchone()[0]
    allergens = len(KOREAN_ALLERGENS)

    print(f"\n  Domain 1: KISCHEM First-Aid")
    print(f"    Records: {kischem:,}")
    print(f"    Content: 증상, 흡입/피부/안구/경구 접촉 응급처치")
    print(f"    Status:  Ready for braille conversion")

    print(f"\n  Domain 2: FDA Drug Labels (OpenFDA)")
    print(f"    Records: {drugs:,}")
    print(f"    Content: 적응증, 경고, 용량, 활성성분, 주의사항")
    print(f"    Status:  Ready for braille conversion")

    print(f"\n  Domain 3: Food Allergen Warnings")
    print(f"    Allergens: {allergens}")
    print(f"    Content: 한국 식품 알레르기 유발성분 22종 경고문")
    print(f"    Status:  Template-based, ready for braille conversion")

    total = kischem + drugs + allergens
    print(f"\n  Total addressable records: {total:,}")
    print(f"{'=' * 70}")

    conn.close()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--kischem', action='store_true')
    parser.add_argument('--drugs', action='store_true')
    parser.add_argument('--food', action='store_true')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--report', action='store_true')
    parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args()

    if args.report or (not args.kischem and not args.drugs and not args.food and not args.all):
        print_report()

    if args.kischem or args.all:
        export_kischem_braille(args.limit)

    if args.drugs or args.all:
        export_drug_braille(args.limit)

    if args.food or args.all:
        export_food_allergen_braille()


if __name__ == '__main__':
    main()

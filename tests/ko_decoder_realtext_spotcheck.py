"""Spot-check Korean decoder behavior on sample MSDS source text."""

from __future__ import annotations

import argparse
import csv
import os
import random
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from eval.similarity import chrf_score, normalized_edit_similarity
from pipeline.ko_braille import encode_korean_braille
from tests.roundtrip_harness import drop_digit_gap
from pipeline.ko_braille_decoder import decode_korean_braille

DEFAULT_DB_PATH = PROJECT_ROOT / 'data' / 'terminology.sample.db'
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / 'results' / 'ko_decoder_realtext_spotcheck.csv'
DEFAULT_SUMMARY_PATH = PROJECT_ROOT / 'results' / 'ko_decoder_realtext_spotcheck_summary.csv'


def extract_text(xml_data: str) -> str:
    root = ET.fromstring(xml_data)
    parts: list[str] = []
    for item in root.findall('.//item'):
        label = (item.findtext('msdsItemNameKor') or '').strip()
        detail = (item.findtext('itemDetail') or '').strip()
        if not detail:
            continue
        parts.append(f'{label}: {detail}' if label else detail)
    return '\n'.join(parts)


def load_all_rows(db_path: Path) -> list[tuple[str, int, str]]:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute('SELECT chem_id, section_no, xml_data FROM msds_details ORDER BY chem_id, section_no')
        return cur.fetchall()
    finally:
        conn.close()


def select_rows(rows: list[tuple[str, int, str]], limit: int, *, sample: bool, seed: int) -> list[tuple[str, int, str]]:
    if sample and len(rows) > limit:
        rng = random.Random(seed)
        return rng.sample(rows, limit)
    return rows[:limit]


def evaluate_rows(rows_in: list[tuple[str, int, str]], *, run_id: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for chem_id, section_no, xml_data in rows_in:
        source = extract_text(xml_data)
        braille = encode_korean_braille(source)
        roundtrip = decode_korean_braille(braille)
        rows.append({
            'run_id': run_id,
            'chem_id': chem_id,
            'section_no': str(section_no),
            'source': source,
            'roundtrip': roundtrip,
            'edit_similarity': f'{normalized_edit_similarity(source, roundtrip):.6f}',
            'chrf': f'{chrf_score(source, roundtrip):.6f}',
            'ok': str(drop_digit_gap(source) == drop_digit_gap(roundtrip)),
        })
    return rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    summary: list[dict[str, str]] = []
    overall_edit = sum(float(row['edit_similarity']) for row in rows) / len(rows) if rows else 0.0
    overall_chrf = sum(float(row['chrf']) for row in rows) / len(rows) if rows else 0.0
    overall_fails = sum(1 for row in rows if row['ok'] != 'True')
    summary.append({'group': 'overall', 'rows': str(len(rows)), 'avg_edit': f'{overall_edit:.6f}', 'avg_chrf': f'{overall_chrf:.6f}', 'fails': str(overall_fails)})

    by_section: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_section[row['section_no']].append(row)
    for section_no in sorted(by_section, key=lambda x: int(x)):
        bucket = by_section[section_no]
        avg_edit = sum(float(row['edit_similarity']) for row in bucket) / len(bucket)
        avg_chrf = sum(float(row['chrf']) for row in bucket) / len(bucket)
        fails = sum(1 for row in bucket if row['ok'] != 'True')
        summary.append({'group': f'sec-{section_no}', 'rows': str(len(bucket)), 'avg_edit': f'{avg_edit:.6f}', 'avg_chrf': f'{avg_chrf:.6f}', 'fails': str(fails)})
    return summary


def print_summary(summary: list[dict[str, str]]) -> None:
    print('summary:')
    print(f"  {'group':<10} {'rows':>4} {'avg_edit':>10} {'avg_chrf':>10} {'fails':>6}")
    print('  ' + '-' * 48)
    for row in summary:
        print(f"  {row['group']:<10} {int(row['rows']):>4} {float(row['avg_edit']):>10.4f} {float(row['avg_chrf']):>10.4f} {int(row['fails']):>6}")


def main() -> None:
    env_db_path = os.environ.get('BRAILLE_MSDS_DB_PATH', '').strip()
    default_db = env_db_path or str(DEFAULT_DB_PATH)
    parser = argparse.ArgumentParser(description='Korean decoder real-text spot-check runner')
    parser.add_argument('--db', default=default_db, help='SQLite DB path (defaults to BRAILLE_MSDS_DB_PATH when set, else sample DB)')
    parser.add_argument('--limit', type=int, default=6, help='Number of msds_details rows to evaluate per run')
    parser.add_argument('--sample', action='store_true', help='Randomly sample rows instead of taking the first N')
    parser.add_argument('--seed', type=int, default=42, help='Random seed when --sample is set')
    parser.add_argument('--repeats', type=int, default=1, help='Number of repeated runs (seed increments per run when sampling)')
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT_PATH), help='Per-row CSV output path')
    parser.add_argument('--summary-output', default=str(DEFAULT_SUMMARY_PATH), help='Summary CSV output path')
    args = parser.parse_args()

    db_path = Path(args.db)
    output_path = Path(args.output)
    summary_output_path = Path(args.summary_output)
    all_db_rows = load_all_rows(db_path)

    rows: list[dict[str, str]] = []
    for repeat_idx in range(args.repeats):
        run_id = f'run-{repeat_idx + 1}'
        selected = select_rows(all_db_rows, args.limit, sample=args.sample, seed=args.seed + repeat_idx)
        rows.extend(evaluate_rows(selected, run_id=run_id))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['run_id','chem_id','section_no','source','roundtrip','edit_similarity','chrf','ok'])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    summary = build_summary(rows)
    with summary_output_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['group', 'rows', 'avg_edit', 'avg_chrf', 'fails'])
        writer.writeheader()
        for row in summary:
            writer.writerow(row)

    failures = [row for row in rows if row['ok'] != 'True']
    print(f'rows={len(rows)} failures={len(failures)} repeats={args.repeats} db={db_path} output={output_path} summary={summary_output_path}')
    print_summary(summary)
    for row in failures[:5]:
        print(f"FAIL run={row['run_id']} chem_id={row['chem_id']} section={row['section_no']} edit={row['edit_similarity']} chrf={row['chrf']}")
        print('SRC:', row['source'].encode('unicode_escape').decode())
        print('RT :', row['roundtrip'].encode('unicode_escape').decode())
        print('---')


if __name__ == '__main__':
    main()

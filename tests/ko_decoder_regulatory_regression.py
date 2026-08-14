"""Focused regulatory regression runner for larger-DB decoder failures."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from eval.similarity import chrf_score, normalized_edit_similarity
from tests.roundtrip_harness import drop_digit_gap
from pipeline.ko_braille import encode_korean_braille
from pipeline.ko_braille_decoder import decode_korean_braille

DEFAULT_INPUT = PROJECT_ROOT / 'data' / 'ko_decoder_regulatory_failures.json'
DEFAULT_OUTPUT = PROJECT_ROOT / 'results' / 'ko_decoder_regulatory_regression.json'
DEFAULT_SUMMARY = PROJECT_ROOT / 'results' / 'ko_decoder_regulatory_regression_summary.csv'


def load_cases(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding='utf-8'))


def evaluate_cases(cases: list[dict]) -> list[dict]:
    rows = []
    for case in cases:
        source = case['source']
        roundtrip = decode_korean_braille(encode_korean_braille(source))
        rows.append({
            'chem_id': case['chem_id'],
            'section_no': str(case['section_no']),
            'source': source,
            'roundtrip': roundtrip,
            'edit_similarity': normalized_edit_similarity(source, roundtrip),
            'chrf': chrf_score(source, roundtrip),
            'ok': drop_digit_gap(source) == drop_digit_gap(roundtrip),
        })
    return rows


def summarize(rows: list[dict]) -> list[dict]:
    buckets = defaultdict(list)
    for row in rows:
        buckets[row['section_no']].append(row)
    summary = []
    overall_fails = sum(1 for row in rows if not row['ok'])
    overall_edit = sum(row['edit_similarity'] for row in rows) / len(rows) if rows else 0.0
    overall_chrf = sum(row['chrf'] for row in rows) / len(rows) if rows else 0.0
    summary.append({'group': 'overall', 'rows': len(rows), 'avg_edit': overall_edit, 'avg_chrf': overall_chrf, 'fails': overall_fails})
    for sec in sorted(buckets, key=int):
        bucket = buckets[sec]
        summary.append({
            'group': f'sec-{sec}',
            'rows': len(bucket),
            'avg_edit': sum(r['edit_similarity'] for r in bucket) / len(bucket),
            'avg_chrf': sum(r['chrf'] for r in bucket) / len(bucket),
            'fails': sum(1 for r in bucket if not r['ok']),
        })
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description='Regulatory-text decoder regression runner')
    parser.add_argument('--input', default=str(DEFAULT_INPUT))
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT))
    parser.add_argument('--summary-output', default=str(DEFAULT_SUMMARY))
    args = parser.parse_args()

    cases = load_cases(Path(args.input))
    rows = evaluate_cases(cases)
    summary = summarize(rows)

    output = Path(args.output)
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')

    import csv
    summary_path = Path(args.summary_output)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['group', 'rows', 'avg_edit', 'avg_chrf', 'fails'])
        writer.writeheader()
        for row in summary:
            writer.writerow({
                'group': row['group'],
                'rows': row['rows'],
                'avg_edit': f"{row['avg_edit']:.6f}",
                'avg_chrf': f"{row['avg_chrf']:.6f}",
                'fails': row['fails'],
            })

    failures = [r for r in rows if not r['ok']]
    print(f'cases={len(rows)} failures={len(failures)} output={output} summary={summary_path}')
    print('summary:')
    print(f"  {'group':<10} {'rows':>4} {'avg_edit':>10} {'avg_chrf':>10} {'fails':>6}")
    print('  ' + '-' * 48)
    for row in summary:
        print(f"  {row['group']:<10} {row['rows']:>4} {row['avg_edit']:>10.4f} {row['avg_chrf']:>10.4f} {row['fails']:>6}")
    for row in failures[:5]:
        print(f"FAIL chem_id={row['chem_id']} sec={row['section_no']} edit={row['edit_similarity']:.6f} chrf={row['chrf']:.6f}")
        print('SRC:', row['source'][:240].encode('unicode_escape').decode())
        print('RT :', row['roundtrip'][:240].encode('unicode_escape').decode())
        print('---')

    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()

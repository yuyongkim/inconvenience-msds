"""Persistent Korean decoder stress cases and CLI runner."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.ko_braille import encode_korean_braille
from tests.roundtrip_harness import drop_digit_gap
from pipeline.ko_braille_decoder import decode_korean_braille

DEFAULT_CASES_PATH = PROJECT_ROOT / 'data' / 'ko_decoder_stress_cases.txt'
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / 'results' / 'ko_decoder_stress_results.csv'
DEFAULT_SUMMARY_PATH = PROJECT_ROOT / 'results' / 'ko_decoder_stress_summary.csv'


def load_cases(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def load_cases_from_path(path: Path) -> list[str]:
    if path.is_dir():
        cases: list[str] = []
        for child in sorted(path.glob('*.txt')):
            cases.extend(load_cases(child))
        return cases
    return load_cases(path)


def classify_case(source: str) -> str:
    if any(ch in source for ch in ['"', '“', '”', '?']):
        return 'quote'
    if any(ch in source for ch in ['(', ')', '*']):
        return 'paren'
    if any(ch.isdigit() for ch in source):
        return 'mixed-numeric'
    if any(ch.isascii() and ch.isalpha() for ch in source):
        return 'mixed-latin'
    return 'hangul'


def run_cases(cases: list[str]) -> list[dict[str, str | bool]]:
    results: list[dict[str, str | bool]] = []
    for source in cases:
        braille = encode_korean_braille(source)
        roundtrip = decode_korean_braille(braille)
        results.append({
            'category': classify_case(source),
            'source': source,
            'roundtrip': roundtrip,
            'ok': drop_digit_gap(roundtrip) == drop_digit_gap(source),
        })
    return results


def build_summary(results: list[dict[str, str | bool]]) -> list[dict[str, str | int]]:
    categories = sorted({str(row['category']) for row in results})
    summary: list[dict[str, str | int]] = []
    for category in categories:
        bucket = [row for row in results if row['category'] == category]
        failures = sum(1 for row in bucket if not row['ok'])
        summary.append({'category': category, 'cases': len(bucket), 'failures': failures})
    summary.append({'category': 'overall', 'cases': len(results), 'failures': sum(1 for row in results if not row['ok'])})
    return summary


def save_results(results: list[dict[str, str | bool]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['category', 'source', 'roundtrip', 'ok'])
        writer.writeheader()
        for row in results:
            writer.writerow(row)


def save_summary(summary: list[dict[str, str | int]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['category', 'cases', 'failures'])
        writer.writeheader()
        for row in summary:
            writer.writerow(row)


def print_summary(summary: list[dict[str, str | int]]) -> None:
    print('summary:')
    print(f"  {'category':<14} {'cases':>5} {'failures':>8}")
    print('  ' + '-' * 30)
    for row in summary:
        print(f"  {str(row['category']):<14} {int(row['cases']):>5} {int(row['failures']):>8}")


def main() -> None:
    parser = argparse.ArgumentParser(description='Korean decoder stress runner')
    parser.add_argument('--cases', default=str(DEFAULT_CASES_PATH), help='UTF-8 case file or directory of .txt case files')
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT_PATH), help='Per-case CSV output path')
    parser.add_argument('--summary-output', default=str(DEFAULT_SUMMARY_PATH), help='Summary CSV output path')
    args = parser.parse_args()

    case_path = Path(args.cases)
    output_path = Path(args.output)
    summary_output_path = Path(args.summary_output)
    results = run_cases(load_cases_from_path(case_path))
    failures = [row for row in results if not row['ok']]
    summary = build_summary(results)

    save_results(results, output_path)
    save_summary(summary, summary_output_path)
    print(f'cases={len(results)} failures={len(failures)} source={case_path} output={output_path} summary={summary_output_path}')
    print_summary(summary)
    for row in failures:
        print('SRC:', row['source'])
        print('RT :', row['roundtrip'])
        print('---')

    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()

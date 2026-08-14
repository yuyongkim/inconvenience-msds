"""Synthetic noisy-braille decoder QA runner."""

from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from eval.similarity import chrf_score, normalized_edit_similarity
from pipeline.ko_braille import encode_korean_braille
from pipeline.ko_braille_decoder import decode_korean_braille
from tests.ko_decoder_stress_runner import load_cases_from_path

DEFAULT_CASES_PATH = PROJECT_ROOT / 'data' / 'ko_decoder_stress'
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / 'results' / 'ko_decoder_noisy_stress.csv'
DEFAULT_SUMMARY_PATH = PROJECT_ROOT / 'results' / 'ko_decoder_noisy_stress_summary.csv'
DEFAULT_RATES = (0.02, 0.05, 0.10)
_BRAILLE_MIN = 0x2801
_BRAILLE_MAX = 0x28FF


def mutate_braille(text: str, rate: float, rng: random.Random) -> str:
    chars = list(text)
    mutable_indices = [i for i, ch in enumerate(chars) if _BRAILLE_MIN <= ord(ch) <= _BRAILLE_MAX]
    flips = max(1, int(len(mutable_indices) * rate)) if mutable_indices else 0
    for idx in rng.sample(mutable_indices, min(flips, len(mutable_indices))):
        original = ord(chars[idx]) - 0x2800
        bit = 1 << rng.randrange(0, 6)
        mutated = original ^ bit
        if mutated == 0:
            mutated = bit
        chars[idx] = chr(0x2800 + mutated)
    return ''.join(chars)


def run_cases(cases: list[str], rates: list[float], seed: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for case_idx, source in enumerate(cases):
        braille = encode_korean_braille(source)
        for rate in rates:
            rng = random.Random(seed + case_idx * 1000 + int(rate * 1000))
            noisy = mutate_braille(braille, rate, rng)
            roundtrip = decode_korean_braille(noisy)
            rows.append({
                'source': source,
                'corruption_rate': f'{rate:.2f}',
                'roundtrip': roundtrip,
                'edit_similarity': f'{normalized_edit_similarity(source, roundtrip):.6f}',
                'chrf': f'{chrf_score(source, roundtrip):.6f}',
            })
    return rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    summary: list[dict[str, str]] = []
    for rate in sorted({row['corruption_rate'] for row in rows}, key=float):
        bucket = [row for row in rows if row['corruption_rate'] == rate]
        avg_edit = sum(float(row['edit_similarity']) for row in bucket) / len(bucket)
        avg_chrf = sum(float(row['chrf']) for row in bucket) / len(bucket)
        summary.append({
            'corruption_rate': rate,
            'cases': str(len(bucket)),
            'avg_edit': f'{avg_edit:.6f}',
            'avg_chrf': f'{avg_chrf:.6f}',
        })
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description='Synthetic noisy-braille decoder QA runner')
    parser.add_argument('--cases', default=str(DEFAULT_CASES_PATH), help='Case file or directory')
    parser.add_argument('--rates', default=','.join(f'{r:.2f}' for r in DEFAULT_RATES), help='Comma-separated corruption rates, e.g. 0.02,0.05,0.10')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument('--summary-output', default=str(DEFAULT_SUMMARY_PATH))
    args = parser.parse_args()

    case_path = Path(args.cases)
    rates = [float(part) for part in args.rates.split(',') if part.strip()]
    rows = run_cases(load_cases_from_path(case_path), rates, args.seed)
    summary = build_summary(rows)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['source', 'corruption_rate', 'roundtrip', 'edit_similarity', 'chrf'])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    summary_output = Path(args.summary_output)
    with summary_output.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['corruption_rate', 'cases', 'avg_edit', 'avg_chrf'])
        writer.writeheader()
        for row in summary:
            writer.writerow(row)

    print(f'cases={len(rows)} source={case_path} output={output_path} summary={summary_output}')
    print('summary:')
    print(f"  {'rate':<8} {'cases':>5} {'avg_edit':>10} {'avg_chrf':>10}")
    print('  ' + '-' * 39)
    for row in summary:
        print(f"  {row['corruption_rate']:<8} {int(row['cases']):>5} {float(row['avg_edit']):>10.4f} {float(row['avg_chrf']):>10.4f}")


if __name__ == '__main__':
    main()

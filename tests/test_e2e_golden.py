"""
English-pipeline to Korean-reference smoke test.

Important:
- This is not a trustworthy KR braille quality benchmark.
- It mixes English decode/correction, external translation, and Korean braille
  encoding, so its KR-side numbers are diagnostics only.
- Translation failures, including silent source-text fallbacks, are reported as
  skipped rows instead of being scored as if they were Korean output.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from eval.similarity import chrf_score, normalized_edit_similarity
from pipeline.corrector import correct_noisy_text
from pipeline.decoder import braille_to_text
from pipeline.encoder import encode_text_to_braille
from pipeline.ko_braille import encode_korean_braille
from pipeline.translator import translate_text


def load_golden(lang: str) -> list[dict]:
    path = PROJECT_ROOT / 'data' / f'golden_braille_roundtrip_{lang}.csv'
    rows = []
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def run_e2e_test(sleep_seconds: float = 0.3) -> list[dict]:
    en_rows = load_golden('en')
    ko_rows = load_golden('ko')
    assert len(en_rows) == len(ko_rows), 'EN/KR golden sets must be same size'

    results = []
    for en_row, ko_row in zip(en_rows, ko_rows):
        sid = en_row['id']
        category = en_row['category']
        en_text = en_row['source_text']
        ko_gold = ko_row['source_text']

        en_braille = encode_text_to_braille(en_text)
        decoded = braille_to_text(en_braille)
        corrected = correct_noisy_text(decoded)
        decode_sim = normalized_edit_similarity(en_text, decoded)

        translation_status = 'ok'
        ko_translated = None
        try:
            ko_translated = translate_text(corrected)
            if sleep_seconds > 0:
                time.sleep(sleep_seconds)
        except Exception as exc:
            translation_status = f'skipped: {exc}'

        if not ko_translated:
            if translation_status == 'ok':
                translation_status = 'skipped: empty translation result'
            ko_translated = None
        elif ko_translated == corrected:
            translation_status = 'skipped: translator returned source text'
            ko_translated = None

        trans_sim = None
        trans_chrf = None
        braille_sim = None
        if ko_translated is not None:
            ko_braille = encode_korean_braille(ko_translated)
            ko_gold_braille = encode_korean_braille(ko_gold)
            trans_sim = normalized_edit_similarity(ko_gold, ko_translated)
            trans_chrf = chrf_score(ko_gold, ko_translated)
            braille_sim = normalized_edit_similarity(ko_gold_braille, ko_braille)
            status = 'OK' if decode_sim >= 0.99 else 'WARN'
            print(
                f"  [{status}] {sid} {category:<8} "
                f"decode={decode_sim:.2f} diag_trans={trans_sim:.2f} diag_braille={braille_sim:.2f}"
            )
        else:
            print(f"  [SKIP] {sid} {category:<8} decode={decode_sim:.2f} {translation_status}")

        results.append({
            'id': sid,
            'category': category,
            'translation_status': translation_status,
            'decode_sim': decode_sim,
            'trans_sim': trans_sim,
            'trans_chrf': trans_chrf,
            'braille_sim': braille_sim,
        })

    return results


def _format_optional(value: float | None, width: int) -> str:
    if value is None:
        return f"{'N/A':>{width}}"
    return f"{value:>{width}.4f}"


def print_summary(results: list[dict], output_path: Path) -> None:
    from collections import defaultdict

    print(f"\n{'=' * 78}")
    print(f"  EN pipeline -> KO reference smoke results ({len(results)} sentences)")
    print('  decode_sim is the only direct benchmark metric in this script.')
    print('  trans_* and braille_sim are diagnostic only.')
    print(f"{'=' * 78}")

    by_category = defaultdict(list)
    for row in results:
        by_category[row['category']].append(row)

    print(f"\n  {'Category':<12} {'N':>4} {'Decode':>8} {'DiagTrans':>10} {'DiagChrF':>10} {'DiagBraille':>12} {'Skipped':>8}")
    print(f"  {'-' * 74}")

    for category, rows in sorted(by_category.items()):
        translated = [row for row in rows if row['trans_sim'] is not None]
        skipped = len(rows) - len(translated)
        avg_decode = sum(row['decode_sim'] for row in rows) / len(rows)
        avg_trans = sum(row['trans_sim'] for row in translated) / len(translated) if translated else None
        avg_chrf = sum(row['trans_chrf'] for row in translated) / len(translated) if translated else None
        avg_braille = sum(row['braille_sim'] for row in translated) / len(translated) if translated else None
        print(
            f"  {category:<12} {len(rows):>4} {avg_decode:>8.4f} "
            f"{_format_optional(avg_trans, 10)} {_format_optional(avg_chrf, 10)} {_format_optional(avg_braille, 12)} {skipped:>8}"
        )

    translated = [row for row in results if row['trans_sim'] is not None]
    skipped = len(results) - len(translated)
    overall_trans = sum(row['trans_sim'] for row in translated) / len(translated) if translated else None
    overall_chrf = sum(row['trans_chrf'] for row in translated) / len(translated) if translated else None
    overall_braille = sum(row['braille_sim'] for row in translated) / len(translated) if translated else None
    print(f"  {'-' * 74}")
    print(
        f"  {'OVERALL':<12} {len(results):>4} {sum(row['decode_sim'] for row in results) / len(results):>8.4f} "
        f"{_format_optional(overall_trans, 10)} {_format_optional(overall_chrf, 10)} {_format_optional(overall_braille, 12)} {skipped:>8}"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                'id',
                'category',
                'translation_status',
                'decode_sim',
                'trans_sim',
                'trans_chrf',
                'braille_sim',
            ],
        )
        writer.writeheader()
        for row in results:
            out_row = row.copy()
            for key in ('decode_sim', 'trans_sim', 'trans_chrf', 'braille_sim'):
                value = out_row[key]
                out_row[key] = '' if value is None else f"{value:.6f}"
            writer.writerow(out_row)
    print(f"\n  Results saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description='EN pipeline to KO reference smoke test')
    parser.add_argument('--sleep-seconds', type=float, default=0.3,
                        help='Delay after successful translation calls (default: 0.3)')
    parser.add_argument('--output', default=str(PROJECT_ROOT / 'results' / 'en_pipeline_translation_smoke.csv'),
                        help='Output CSV path (diagnostic only)')
    args = parser.parse_args()

    results = run_e2e_test(sleep_seconds=args.sleep_seconds)
    print_summary(results, Path(args.output))


if __name__ == '__main__':
    main()

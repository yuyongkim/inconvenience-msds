"""
Round-trip driver for the golden English and Korean text sets.

This compatibility entrypoint keeps the old filename but now runs the
language-specific harness explicitly:
    - EN uses pipeline.decoder.braille_to_text
    - KO uses pipeline.ko_braille_decoder.decode_korean_braille
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.roundtrip_harness import (
    compute_category_stats,
    print_results,
    run_roundtrip_suite,
    save_results_csv,
)


def main() -> None:
    parser = argparse.ArgumentParser(description='Golden-set round-trip test driver')
    parser.add_argument('--lang', default='all', choices=['en', 'ko', 'all'],
                        help='Language suite to run (default: all)')
    parser.add_argument('--output', default=None,
                        help='Combined output CSV path (optional)')
    parser.add_argument('--strip-whitespace', action='store_true')
    parser.add_argument('--strip-punctuation', action='store_true')
    parser.add_argument('--data-dir', default=str(PROJECT_ROOT / 'data'),
                        help='Directory containing golden CSV files')
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    langs = ['en', 'ko'] if args.lang == 'all' else [args.lang]
    all_results = []

    for lang in langs:
        csv_path = data_dir / f'golden_braille_roundtrip_{lang}.csv'
        if not csv_path.exists():
            print(f"WARNING: {csv_path} not found, skipping {lang}")
            continue

        results = run_roundtrip_suite(
            lang,
            data_dir=data_dir,
            strip_whitespace=args.strip_whitespace,
            strip_punctuation=args.strip_punctuation,
        )
        stats = compute_category_stats(results)
        print_results(results, stats, lang)
        all_results.extend(results)

    if args.output and all_results:
        save_results_csv(all_results, Path(args.output))


if __name__ == '__main__':
    main()

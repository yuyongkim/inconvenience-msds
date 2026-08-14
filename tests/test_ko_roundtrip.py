"""
Dedicated Korean round-trip runner.

This suite explicitly uses the Korean decoder path
(`pipeline.ko_braille_decoder.decode_korean_braille`) so KR evaluation does
not accidentally report English-decoder results.
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
    parser = argparse.ArgumentParser(description='Korean golden-set round-trip test')
    parser.add_argument('--output', default=None, help='Output CSV path (optional)')
    parser.add_argument('--strip-whitespace', action='store_true')
    parser.add_argument('--strip-punctuation', action='store_true')
    parser.add_argument('--data-dir', default=str(PROJECT_ROOT / 'data'))
    args = parser.parse_args()

    results = run_roundtrip_suite(
        'ko',
        data_dir=Path(args.data_dir),
        strip_whitespace=args.strip_whitespace,
        strip_punctuation=args.strip_punctuation,
    )
    stats = compute_category_stats(results)
    print_results(results, stats, 'ko')

    if args.output:
        save_results_csv(results, Path(args.output))


if __name__ == '__main__':
    main()

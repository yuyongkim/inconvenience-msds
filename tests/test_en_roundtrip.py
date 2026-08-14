"""
Dedicated English round-trip runner.

This script exists so English and Korean round-trip evaluation can be run
as separate, named suites instead of a single mixed report.
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
    parser = argparse.ArgumentParser(description='English golden-set round-trip test')
    parser.add_argument('--output', default=None, help='Output CSV path (optional)')
    parser.add_argument('--strip-whitespace', action='store_true')
    parser.add_argument('--strip-punctuation', action='store_true')
    parser.add_argument('--data-dir', default=str(PROJECT_ROOT / 'data'))
    args = parser.parse_args()

    results = run_roundtrip_suite(
        'en',
        data_dir=Path(args.data_dir),
        strip_whitespace=args.strip_whitespace,
        strip_punctuation=args.strip_punctuation,
    )
    stats = compute_category_stats(results)
    print_results(results, stats, 'en')

    if args.output:
        save_results_csv(results, Path(args.output))


if __name__ == '__main__':
    main()

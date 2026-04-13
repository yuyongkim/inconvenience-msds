"""
BrailleIO Round-trip Test Script (A)

Reads golden CSV datasets, runs encode→decode round-trip for each sentence,
computes similarity scores, and outputs per-sentence + per-category results.

Usage:
    python tests/test_braille_roundtrip.py --lang en
    python tests/test_braille_roundtrip.py --lang ko
    python tests/test_braille_roundtrip.py --lang all --output results/roundtrip_results.csv

Requires:
    - A braille encode/decode module. If not available, uses stub functions.
    - Golden CSV files in data/ directory.
"""

import argparse
import csv
import sys
from pathlib import Path
from collections import defaultdict

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from eval.similarity import normalized_edit_similarity, chrf_score


# ---------------------------------------------------------------------------
# Braille encode/decode interface (stub – replace with real implementation)
# ---------------------------------------------------------------------------

from pipeline.encoder import encode_text_to_braille
from pipeline.decoder import braille_to_text
from pipeline.ko_braille import encode_korean_braille


def encode_braille(text: str, lang: str = 'en') -> str:
    if lang == 'ko':
        return encode_korean_braille(text)
    return encode_text_to_braille(text)


def decode_braille(braille: str, lang: str = 'en') -> str:
    return braille_to_text(braille)


# ---------------------------------------------------------------------------
# Core test logic
# ---------------------------------------------------------------------------

def run_roundtrip_test(csv_path: str, lang: str, *,
                       strip_whitespace: bool = False,
                       strip_punctuation: bool = False) -> list[dict]:
    """
    Run round-trip test on a golden CSV.

    Returns list of result dicts with keys:
        id, category, source_text, braille, roundtrip_text,
        sim_edit, sim_chrf
    """
    results = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row['id']
            source = row['source_text']
            category = row['category']

            # Round-trip
            braille = encode_braille(source, lang=lang)
            roundtrip = decode_braille(braille, lang=lang)

            # Similarity
            sim_edit = normalized_edit_similarity(
                source, roundtrip,
                strip_whitespace=strip_whitespace,
                strip_punctuation=strip_punctuation,
            )
            sim_chrf = chrf_score(source, roundtrip)

            results.append({
                'id': sid,
                'category': category,
                'source_text': source,
                'braille': braille,
                'roundtrip_text': roundtrip,
                'sim_edit': round(sim_edit, 4),
                'sim_chrf': round(sim_chrf, 4),
            })

    return results


def compute_category_stats(results: list[dict]) -> dict:
    """Compute per-category average scores."""
    buckets = defaultdict(list)
    for r in results:
        buckets[r['category']].append(r)

    stats = {}
    for cat, rows in sorted(buckets.items()):
        n = len(rows)
        avg_edit = sum(r['sim_edit'] for r in rows) / n
        avg_chrf = sum(r['sim_chrf'] for r in rows) / n
        stats[cat] = {
            'count': n,
            'avg_sim_edit': round(avg_edit, 4),
            'avg_sim_chrf': round(avg_chrf, 4),
        }
    return stats


def print_results(results: list[dict], stats: dict, lang: str):
    """Print results to console."""
    print(f"\n{'='*70}")
    print(f"  Round-trip Results [{lang.upper()}]  ({len(results)} sentences)")
    print(f"{'='*70}")

    print(f"\n{'ID':<10} {'Category':<12} {'Edit Sim':>10} {'ChrF':>10}  Source (truncated)")
    print('-' * 70)
    for r in results:
        src_trunc = r['source_text'][:35] + ('...' if len(r['source_text']) > 35 else '')
        print(f"{r['id']:<10} {r['category']:<12} {r['sim_edit']:>10.4f} {r['sim_chrf']:>10.4f}  {src_trunc}")

    print(f"\n{'Category':<15} {'Count':>6} {'Avg Edit':>10} {'Avg ChrF':>10}")
    print('-' * 45)
    for cat, s in stats.items():
        print(f"{cat:<15} {s['count']:>6} {s['avg_sim_edit']:>10.4f} {s['avg_sim_chrf']:>10.4f}")

    # Overall
    overall_edit = sum(r['sim_edit'] for r in results) / len(results)
    overall_chrf = sum(r['sim_chrf'] for r in results) / len(results)
    print('-' * 45)
    print(f"{'OVERALL':<15} {len(results):>6} {overall_edit:>10.4f} {overall_chrf:>10.4f}")


def save_results_csv(results: list[dict], output_path: str):
    """Save per-sentence results to CSV."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'id', 'category', 'source_text', 'roundtrip_text', 'sim_edit', 'sim_chrf'
        ])
        writer.writeheader()
        for r in results:
            writer.writerow({
                'id': r['id'],
                'category': r['category'],
                'source_text': r['source_text'],
                'roundtrip_text': r['roundtrip_text'],
                'sim_edit': r['sim_edit'],
                'sim_chrf': r['sim_chrf'],
            })
    print(f"\nResults saved to {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='BrailleIO Round-trip Test')
    parser.add_argument('--lang', default='all', choices=['en', 'ko', 'all'],
                        help='Language to test (default: all)')
    parser.add_argument('--output', default=None,
                        help='Output CSV path (optional)')
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

        results = run_roundtrip_test(
            str(csv_path), lang,
            strip_whitespace=args.strip_whitespace,
            strip_punctuation=args.strip_punctuation,
        )
        stats = compute_category_stats(results)
        print_results(results, stats, lang)
        all_results.extend(results)

    if args.output and all_results:
        save_results_csv(all_results, args.output)


if __name__ == '__main__':
    main()

"""
Noise Correction Evaluation Script (B)

Reads noise_correction_eval_en.csv, optionally calls LLM corrector to fill
corrected_en, computes similarity metrics, and outputs results + statistics.

Usage:
    # With pre-filled corrected_en:
    python eval/run_noise_correction_eval.py --input data/noise_correction_eval_en.csv

    # With LLM correction (requires API key):
    python eval/run_noise_correction_eval.py --input data/noise_correction_eval_en.csv --run-llm

    # Custom output path:
    python eval/run_noise_correction_eval.py --input data/noise_correction_eval_en.csv \
                                              --output results/noise_correction_results.csv
"""

import argparse
import csv
import sys
import statistics
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from eval.similarity import normalized_edit_similarity, chrf_score


# ---------------------------------------------------------------------------
# Noise Corrector interface
# ---------------------------------------------------------------------------

def correct_with_llm(noisy_text: str, **kwargs) -> str:
    """Call the rule-based noise corrector."""
    from pipeline.corrector import correct_noisy_text
    return correct_noisy_text(noisy_text)


# ---------------------------------------------------------------------------
# Evaluation logic
# ---------------------------------------------------------------------------

def evaluate_row(clean: str, noisy: str, corrected: str) -> dict:
    """Compute similarity metrics for a single row."""
    sim_clean_noisy_edit = normalized_edit_similarity(clean, noisy)
    sim_clean_corrected_edit = normalized_edit_similarity(clean, corrected)
    delta_edit = sim_clean_corrected_edit - sim_clean_noisy_edit

    sim_clean_noisy_chrf = chrf_score(clean, noisy)
    sim_clean_corrected_chrf = chrf_score(clean, corrected)
    delta_chrf = sim_clean_corrected_chrf - sim_clean_noisy_chrf

    return {
        'sim_clean_noisy': round(sim_clean_noisy_edit, 4),
        'sim_clean_corrected': round(sim_clean_corrected_edit, 4),
        'delta_sim': round(delta_edit, 4),
        'chrf_clean_noisy': round(sim_clean_noisy_chrf, 4),
        'chrf_clean_corrected': round(sim_clean_corrected_chrf, 4),
        'delta_chrf': round(delta_chrf, 4),
    }


def run_evaluation(input_path: str, run_llm: bool = False, mode: str = 'auto') -> list[dict]:
    """Run noise correction evaluation on the input CSV."""
    results = []

    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row['id']
            clean = row['clean_en']
            noisy = row['noisy_en']
            corrected = row.get('corrected_en', '').strip()
            noise_type = row['noise_type']

            # If corrected is empty and run_llm is True, call corrector
            if not corrected and run_llm:
                corrected = correct_with_llm(noisy, mode=mode)
            elif not corrected:
                # Use noisy as-is (baseline: no correction)
                corrected = noisy

            metrics = evaluate_row(clean, noisy, corrected)

            results.append({
                'id': sid,
                'noise_type': noise_type,
                'clean_en': clean,
                'noisy_en': noisy,
                'corrected_en': corrected,
                **metrics,
            })

    return results


def compute_stats(results: list[dict]) -> dict:
    """Compute aggregate statistics."""
    stats = {}

    # Overall
    deltas = [r['delta_sim'] for r in results]
    deltas_chrf = [r['delta_chrf'] for r in results]
    stats['overall'] = {
        'count': len(results),
        'avg_delta_sim': round(statistics.mean(deltas), 4) if deltas else 0,
        'std_delta_sim': round(statistics.stdev(deltas), 4) if len(deltas) > 1 else 0,
        'positive_ratio': round(sum(1 for d in deltas if d > 0) / len(deltas), 4) if deltas else 0,
        'avg_delta_chrf': round(statistics.mean(deltas_chrf), 4) if deltas_chrf else 0,
    }

    # Per noise_type
    by_type = defaultdict(list)
    for r in results:
        by_type[r['noise_type']].append(r)

    stats['by_type'] = {}
    for ntype, rows in sorted(by_type.items()):
        d = [r['delta_sim'] for r in rows]
        dc = [r['delta_chrf'] for r in rows]
        stats['by_type'][ntype] = {
            'count': len(rows),
            'avg_delta_sim': round(statistics.mean(d), 4),
            'std_delta_sim': round(statistics.stdev(d), 4) if len(d) > 1 else 0,
            'positive_ratio': round(sum(1 for x in d if x > 0) / len(d), 4),
            'avg_delta_chrf': round(statistics.mean(dc), 4),
        }

    return stats


def print_stats(stats: dict):
    """Print statistics to console."""
    print(f"\n{'='*70}")
    print("  Noise Correction Evaluation Results")
    print(f"{'='*70}")

    o = stats['overall']
    print(f"\n  Overall ({o['count']} samples):")
    print(f"    Avg delta_sim (edit):  {o['avg_delta_sim']:+.4f}  (std: {o['std_delta_sim']:.4f})")
    print(f"    Avg delta_sim (chrF):  {o['avg_delta_chrf']:+.4f}")
    print(f"    Positive delta ratio:  {o['positive_ratio']:.2%}")

    print(f"\n  {'Noise Type':<25} {'Count':>6} {'Avg Δ Edit':>12} {'Std':>8} {'Δ>0':>8} {'Avg Δ ChrF':>12}")
    print('  ' + '-' * 75)
    for ntype, s in stats['by_type'].items():
        print(f"  {ntype:<25} {s['count']:>6} {s['avg_delta_sim']:>+12.4f} {s['std_delta_sim']:>8.4f} "
              f"{s['positive_ratio']:>7.0%} {s['avg_delta_chrf']:>+12.4f}")


def save_results_csv(results: list[dict], output_path: str):
    """Save detailed results to CSV."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'id', 'noise_type', 'sim_clean_noisy', 'sim_clean_corrected', 'delta_sim',
            'chrf_clean_noisy', 'chrf_clean_corrected', 'delta_chrf',
        ])
        writer.writeheader()
        for r in results:
            writer.writerow({k: r[k] for k in writer.fieldnames})
    print(f"\nResults saved to {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Noise Correction Evaluation')
    parser.add_argument('--input', required=True, help='Input CSV path')
    parser.add_argument('--output', default='results/noise_correction_results.csv',
                        help='Output CSV path')
    parser.add_argument('--run-llm', action='store_true',
                        help='Run corrector for empty corrected_en rows')
    parser.add_argument('--mode', default='auto', choices=['auto', 'llm', 'rules'],
                        help='Correction mode: auto/llm/rules (default: auto)')
    args = parser.parse_args()

    print(f"Loading data from {args.input}...")
    print(f"Correction mode: {args.mode}")
    results = run_evaluation(args.input, run_llm=args.run_llm, mode=args.mode)
    stats = compute_stats(results)
    print_stats(stats)
    save_results_csv(results, args.output)


if __name__ == '__main__':
    main()

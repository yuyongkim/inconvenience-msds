"""
End-to-End Braille-to-Braille Evaluation Script (C)

Compares Baseline vs Proposed pipeline outputs across three metrics:
  1. text_sim_score  - Semantic quality (decoded braille vs gold Korean text)
  2. structure_f1    - Document structure preservation
  3. rule_violation_rate - Korean braille rule compliance

Usage:
    python eval/run_e2e_eval.py --config eval/e2e_config.json
    python eval/run_e2e_eval.py --config eval/e2e_config.json --output results/e2e_eval_results.csv

Config JSON format:
    {
        "documents": [
            {
                "doc_id": "d01",
                "gold_ko_text_path": "data/e2e/d01_gold_ko.txt",
                "gold_structure_path": "data/e2e/d01_gold_structure.json",
                "baseline_ko_braille_path": "data/e2e/d01_baseline_ko.brl",
                "proposed_ko_braille_path": "data/e2e/d01_proposed_ko.brl"
            }
        ]
    }
"""

import argparse
import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from eval.similarity import normalized_edit_similarity, chrf_score
from eval.rule_checker import check_all_rules


# ---------------------------------------------------------------------------
# Braille decode interface (stub)
# ---------------------------------------------------------------------------

def decode_ko_braille(braille_text: str) -> str:
    """Decode Korean braille to Korean text. Stub – replace with real module."""
    try:
        from braille_io import decode_braille
        return decode_braille(braille_text, lang='ko')
    except ImportError:
        return braille_text


# ---------------------------------------------------------------------------
# Metric 1: Text Similarity Score
# ---------------------------------------------------------------------------

def compute_text_sim_score(gold_text: str, braille_output: str) -> float:
    """
    Decode braille output to text, then compare with gold text.
    Uses chrF as the primary metric.
    """
    decoded = decode_ko_braille(braille_output)
    return chrf_score(gold_text, decoded)


# ---------------------------------------------------------------------------
# Metric 2: Structure F1
# ---------------------------------------------------------------------------

def extract_structure_vector(text: str) -> dict:
    """
    Extract document structure counts from text.
    Simple heuristic approach:
      - para_count: number of paragraph breaks (double newlines or distinct blocks)
      - list_count: lines starting with bullets, numbers, or list markers
      - table_count: blocks with tab-separated or pipe-separated columns
      - math_count: lines containing math-like patterns
    """
    lines = text.strip().split('\n')
    para_count = 0
    list_count = 0
    table_count = 0
    math_count = 0

    in_paragraph = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_paragraph:
                para_count += 1
                in_paragraph = False
            continue

        in_paragraph = True

        # List detection
        if (stripped.startswith(('-', '*', '+')) or
            (len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in '.)')):
            list_count += 1

        # Table detection (pipes or multiple tabs)
        if '|' in stripped or stripped.count('\t') >= 2:
            table_count += 1

        # Math detection
        import re
        if re.search(r'[=+\-*/^].*\d|\\frac|\\sum|\\int|x\^|f\(x\)', stripped):
            math_count += 1

    if in_paragraph:
        para_count += 1

    return {
        'para_count': para_count,
        'list_count': list_count,
        'table_count': table_count,
        'math_count': math_count,
    }


def compute_structure_f1(gold_structure: dict, system_structure: dict) -> float:
    """
    Compute structure F1 based on block count vectors.

    For each block type, compute min(gold, sys)/max(gold, sys) as element-wise agreement,
    then average across all types.
    """
    keys = ['para_count', 'list_count', 'table_count', 'math_count']
    agreements = []

    for k in keys:
        g = gold_structure.get(k, 0)
        s = system_structure.get(k, 0)
        if g == 0 and s == 0:
            agreements.append(1.0)  # Both agree on zero
        elif g == 0 or s == 0:
            agreements.append(0.0)  # One has blocks, other doesn't
        else:
            agreements.append(min(g, s) / max(g, s))

    return sum(agreements) / len(agreements) if agreements else 0.0


# ---------------------------------------------------------------------------
# Metric 3: Rule Violation Rate (delegated to rule_checker)
# ---------------------------------------------------------------------------

def compute_rule_violation_rate(braille_text: str) -> float:
    """Compute rule violations per 1,000 braille cells."""
    report = check_all_rules(braille_text)
    return report['violation_rate_per_1000']


# ---------------------------------------------------------------------------
# Document evaluation
# ---------------------------------------------------------------------------

def evaluate_document(doc_config: dict) -> dict:
    """Evaluate a single document across all three metrics."""
    doc_id = doc_config['doc_id']

    # Load gold text
    gold_text = ''
    gold_text_path = doc_config.get('gold_ko_text_path')
    if gold_text_path and Path(gold_text_path).exists():
        gold_text = Path(gold_text_path).read_text(encoding='utf-8')

    # Load gold structure (or extract from gold text)
    gold_structure_path = doc_config.get('gold_structure_path')
    if gold_structure_path and Path(gold_structure_path).exists():
        with open(gold_structure_path, 'r', encoding='utf-8') as f:
            gold_structure = json.load(f)
    else:
        gold_structure = extract_structure_vector(gold_text)

    # Load system outputs
    baseline_braille = ''
    proposed_braille = ''
    baseline_path = doc_config.get('baseline_ko_braille_path')
    proposed_path = doc_config.get('proposed_ko_braille_path')
    if baseline_path and Path(baseline_path).exists():
        baseline_braille = Path(baseline_path).read_text(encoding='utf-8')
    if proposed_path and Path(proposed_path).exists():
        proposed_braille = Path(proposed_path).read_text(encoding='utf-8')

    result = {'doc_id': doc_id}

    # Metric 1: Text similarity
    if gold_text:
        result['text_sim_score_baseline'] = round(
            compute_text_sim_score(gold_text, baseline_braille), 4) if baseline_braille else 0.0
        result['text_sim_score_proposed'] = round(
            compute_text_sim_score(gold_text, proposed_braille), 4) if proposed_braille else 0.0
    else:
        result['text_sim_score_baseline'] = None
        result['text_sim_score_proposed'] = None

    # Metric 2: Structure F1
    baseline_structure = extract_structure_vector(decode_ko_braille(baseline_braille))
    proposed_structure = extract_structure_vector(decode_ko_braille(proposed_braille))
    result['structure_f1_baseline'] = round(
        compute_structure_f1(gold_structure, baseline_structure), 4)
    result['structure_f1_proposed'] = round(
        compute_structure_f1(gold_structure, proposed_structure), 4)

    # Metric 3: Rule violation rate
    result['rule_violation_rate_baseline'] = round(
        compute_rule_violation_rate(baseline_braille), 2) if baseline_braille else 0.0
    result['rule_violation_rate_proposed'] = round(
        compute_rule_violation_rate(proposed_braille), 2) if proposed_braille else 0.0

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def print_results(results: list[dict]):
    """Print evaluation results to console."""
    print(f"\n{'='*90}")
    print("  End-to-End Evaluation Results (Baseline vs Proposed)")
    print(f"{'='*90}")

    header = (f"  {'DocID':<8} {'TextSim BL':>12} {'TextSim PR':>12} "
              f"{'StructF1 BL':>12} {'StructF1 PR':>12} "
              f"{'RuleViol BL':>12} {'RuleViol PR':>12}")
    print(header)
    print('  ' + '-' * 86)

    for r in results:
        ts_bl = f"{r['text_sim_score_baseline']:.4f}" if r['text_sim_score_baseline'] is not None else 'N/A'
        ts_pr = f"{r['text_sim_score_proposed']:.4f}" if r['text_sim_score_proposed'] is not None else 'N/A'
        print(f"  {r['doc_id']:<8} {ts_bl:>12} {ts_pr:>12} "
              f"{r['structure_f1_baseline']:>12.4f} {r['structure_f1_proposed']:>12.4f} "
              f"{r['rule_violation_rate_baseline']:>12.2f} {r['rule_violation_rate_proposed']:>12.2f}")

    # Averages
    n = len(results)
    if n > 0:
        fields = ['text_sim_score_baseline', 'text_sim_score_proposed',
                   'structure_f1_baseline', 'structure_f1_proposed',
                   'rule_violation_rate_baseline', 'rule_violation_rate_proposed']
        avgs = {}
        for f_name in fields:
            vals = [r[f_name] for r in results if r[f_name] is not None]
            avgs[f_name] = sum(vals) / len(vals) if vals else 0
        print('  ' + '-' * 86)
        ts_bl = f"{avgs['text_sim_score_baseline']:.4f}"
        ts_pr = f"{avgs['text_sim_score_proposed']:.4f}"
        print(f"  {'AVG':<8} {ts_bl:>12} {ts_pr:>12} "
              f"{avgs['structure_f1_baseline']:>12.4f} {avgs['structure_f1_proposed']:>12.4f} "
              f"{avgs['rule_violation_rate_baseline']:>12.2f} {avgs['rule_violation_rate_proposed']:>12.2f}")


def save_results_csv(results: list[dict], output_path: str):
    """Save results to CSV."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        'doc_id',
        'text_sim_score_baseline', 'text_sim_score_proposed',
        'structure_f1_baseline', 'structure_f1_proposed',
        'rule_violation_rate_baseline', 'rule_violation_rate_proposed',
    ]
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nResults saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='End-to-End Braille Evaluation')
    parser.add_argument('--config', required=True,
                        help='JSON config file listing documents to evaluate')
    parser.add_argument('--output', default='results/e2e_eval_results.csv',
                        help='Output CSV path')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)

    results = []
    for doc_cfg in config['documents']:
        print(f"Evaluating {doc_cfg['doc_id']}...")
        result = evaluate_document(doc_cfg)
        results.append(result)

    print_results(results)
    save_results_csv(results, args.output)


if __name__ == '__main__':
    main()

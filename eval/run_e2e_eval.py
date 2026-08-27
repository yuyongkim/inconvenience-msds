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

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from eval.korean_decoder import DECODER_QUALNAME, decode_ko_braille_strict
from eval.rule_checker import check_all_rules
from eval.similarity import chrf_score, normalized_edit_similarity


def resolve_project_path(path_str: str | None) -> Path | None:
    """Resolve config paths relative to the project root."""
    if path_str in (None, ''):
        return None

    path = Path(path_str)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def read_required_text(path_str: str | None, *, label: str, doc_id: str) -> str:
    path = resolve_project_path(path_str)
    if path is None:
        raise FileNotFoundError(f"{doc_id}: missing required path for {label}")
    if not path.exists():
        raise FileNotFoundError(f"{doc_id}: missing {label}: {path}")
    return path.read_text(encoding='utf-8')


def read_optional_json(path_str: str | None, *, doc_id: str) -> dict | None:
    path = resolve_project_path(path_str)
    if path is None:
        return None
    if not path.exists():
        raise FileNotFoundError(f"{doc_id}: missing gold structure file: {path}")
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def decode_ko_braille(braille_text: str) -> str:
    """Decode Korean braille using the strict evaluation decoder path."""
    return decode_ko_braille_strict(braille_text)


def compute_text_metrics(gold_text: str, decoded_text: str) -> dict[str, float]:
    """Measure decoded-text quality separately from braille rule compliance."""
    return {
        'text_sim_score': chrf_score(gold_text, decoded_text),
        'decoded_text_edit_similarity': normalized_edit_similarity(gold_text, decoded_text),
    }


def extract_structure_vector(text: str) -> dict:
    """Extract simple document structure counts from text."""
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

        if stripped.startswith(('-', '*', '+')) or (
            len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in '.)'
        ):
            list_count += 1

        if '|' in stripped or stripped.count('\t') >= 2:
            table_count += 1

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
    """Compute structure F1 based on block count vectors."""
    keys = ['para_count', 'list_count', 'table_count', 'math_count']
    agreements = []

    for key in keys:
        gold_value = gold_structure.get(key, 0)
        system_value = system_structure.get(key, 0)
        if gold_value == 0 and system_value == 0:
            agreements.append(1.0)
        elif gold_value == 0 or system_value == 0:
            agreements.append(0.0)
        else:
            agreements.append(min(gold_value, system_value) / max(gold_value, system_value))

    return sum(agreements) / len(agreements) if agreements else 0.0


def compute_rule_violation_rate(braille_text: str) -> float:
    """Compute rule violations per 1,000 braille cells."""
    report = check_all_rules(braille_text)
    return report['violation_rate_per_1000']


def evaluate_document(doc_config: dict) -> dict:
    """Evaluate a single document across all three metrics."""
    doc_id = doc_config['doc_id']
    gold_text = read_required_text(
        doc_config.get('gold_ko_text_path'),
        label='gold_ko_text_path',
        doc_id=doc_id,
    )
    gold_structure = read_optional_json(doc_config.get('gold_structure_path'), doc_id=doc_id)
    if gold_structure is None:
        gold_structure = extract_structure_vector(gold_text)

    baseline_braille = read_required_text(
        doc_config.get('baseline_ko_braille_path'),
        label='baseline_ko_braille_path',
        doc_id=doc_id,
    )
    proposed_braille = read_required_text(
        doc_config.get('proposed_ko_braille_path'),
        label='proposed_ko_braille_path',
        doc_id=doc_id,
    )

    baseline_text = decode_ko_braille(baseline_braille)
    proposed_text = decode_ko_braille(proposed_braille)

    baseline_metrics = compute_text_metrics(gold_text, baseline_text)
    proposed_metrics = compute_text_metrics(gold_text, proposed_text)

    return {
        'doc_id': doc_id,
        'text_sim_score_baseline': round(baseline_metrics['text_sim_score'], 4),
        'text_sim_score_proposed': round(proposed_metrics['text_sim_score'], 4),
        'decoded_text_edit_similarity_baseline': round(
            baseline_metrics['decoded_text_edit_similarity'], 4
        ),
        'decoded_text_edit_similarity_proposed': round(
            proposed_metrics['decoded_text_edit_similarity'], 4
        ),
        'structure_f1_baseline': round(
            compute_structure_f1(gold_structure, extract_structure_vector(baseline_text)), 4
        ),
        'structure_f1_proposed': round(
            compute_structure_f1(gold_structure, extract_structure_vector(proposed_text)), 4
        ),
        'rule_violation_rate_baseline': round(compute_rule_violation_rate(baseline_braille), 2),
        'rule_violation_rate_proposed': round(compute_rule_violation_rate(proposed_braille), 2),
    }


def print_results(results: list[dict]) -> None:
    """Print evaluation results to console."""
    print(f"\n{'=' * 122}")
    print('  End-to-End Evaluation Results (Baseline vs Proposed)')
    print(f'  Decoder: {DECODER_QUALNAME}')
    print(f"{'=' * 122}")

    header = (
        f"  {'DocID':<8} {'TextSim BL':>12} {'TextSim PR':>12} "
        f"{'EditSim BL':>12} {'EditSim PR':>12} "
        f"{'StructF1 BL':>12} {'StructF1 PR':>12} "
        f"{'RuleViol BL':>12} {'RuleViol PR':>12}"
    )
    print(header)
    print('  ' + '-' * 118)

    for row in results:
        print(
            f"  {row['doc_id']:<8} {row['text_sim_score_baseline']:>12.4f} {row['text_sim_score_proposed']:>12.4f} "
            f"{row['decoded_text_edit_similarity_baseline']:>12.4f} {row['decoded_text_edit_similarity_proposed']:>12.4f} "
            f"{row['structure_f1_baseline']:>12.4f} {row['structure_f1_proposed']:>12.4f} "
            f"{row['rule_violation_rate_baseline']:>12.2f} {row['rule_violation_rate_proposed']:>12.2f}"
        )

    if results:
        fields = [
            'text_sim_score_baseline',
            'text_sim_score_proposed',
            'decoded_text_edit_similarity_baseline',
            'decoded_text_edit_similarity_proposed',
            'structure_f1_baseline',
            'structure_f1_proposed',
            'rule_violation_rate_baseline',
            'rule_violation_rate_proposed',
        ]
        averages = {
            field: sum(row[field] for row in results) / len(results)
            for field in fields
        }
        print('  ' + '-' * 118)
        print(
            f"  {'AVG':<8} {averages['text_sim_score_baseline']:>12.4f} {averages['text_sim_score_proposed']:>12.4f} "
            f"{averages['decoded_text_edit_similarity_baseline']:>12.4f} {averages['decoded_text_edit_similarity_proposed']:>12.4f} "
            f"{averages['structure_f1_baseline']:>12.4f} {averages['structure_f1_proposed']:>12.4f} "
            f"{averages['rule_violation_rate_baseline']:>12.2f} {averages['rule_violation_rate_proposed']:>12.2f}"
        )


def save_results_csv(results: list[dict], output_path: str) -> None:
    """Save results to CSV."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        'doc_id',
        'text_sim_score_baseline',
        'text_sim_score_proposed',
        'decoded_text_edit_similarity_baseline',
        'decoded_text_edit_similarity_proposed',
        'structure_f1_baseline',
        'structure_f1_proposed',
        'rule_violation_rate_baseline',
        'rule_violation_rate_proposed',
    ]
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nResults saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description='End-to-End Braille Evaluation')
    parser.add_argument('--config', required=True, help='JSON config file listing documents to evaluate')
    parser.add_argument('--output', default='results/e2e_eval_results.csv', help='Output CSV path')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)

    results = []
    for doc_cfg in config['documents']:
        print(f"Evaluating {doc_cfg['doc_id']}...")
        results.append(evaluate_document(doc_cfg))

    print_results(results)
    save_results_csv(results, args.output)


if __name__ == '__main__':
    main()

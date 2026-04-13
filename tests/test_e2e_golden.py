"""
End-to-End Golden Set Test.

Uses the parallel EN/KR golden sets (45 sentences each) to test
the full pipeline: EN text → EN braille → decode → correct → translate → compare with KR gold.

This is the most rigorous test we can run without external data.
"""

import csv
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.encoder import encode_text_to_braille
from pipeline.decoder import braille_to_text
from pipeline.corrector import correct_noisy_text
from pipeline.translator import translate_text
from pipeline.ko_braille import encode_korean_braille
from eval.similarity import normalized_edit_similarity, chrf_score


def load_golden(lang: str) -> list[dict]:
    path = PROJECT_ROOT / 'data' / f'golden_braille_roundtrip_{lang}.csv'
    rows = []
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def run_e2e_test():
    en_rows = load_golden('en')
    ko_rows = load_golden('ko')

    assert len(en_rows) == len(ko_rows), "EN/KR golden sets must be same size"

    results = []

    for en_row, ko_row in zip(en_rows, ko_rows):
        sid = en_row['id']
        cat = en_row['category']
        en_text = en_row['source_text']
        ko_gold = ko_row['source_text']

        # Stage 1: Encode EN text → braille
        en_braille = encode_text_to_braille(en_text)

        # Stage 2: Decode braille → EN text
        decoded = braille_to_text(en_braille)

        # Stage 3: Correct
        corrected = correct_noisy_text(decoded)

        # Stage 4: Translate EN → KR
        try:
            ko_translated = translate_text(corrected)
            time.sleep(0.3)  # rate limit
        except Exception as e:
            print(f"  [{sid}] Translation failed: {e}")
            ko_translated = corrected

        # Stage 5: Encode KR → braille
        ko_braille = encode_korean_braille(ko_translated)

        # Also encode gold KR for comparison
        ko_gold_braille = encode_korean_braille(ko_gold)

        # Metrics
        # 1. Decode accuracy (EN roundtrip)
        decode_sim = normalized_edit_similarity(en_text, decoded)

        # 2. Translation quality (KR translated vs KR gold)
        trans_sim = normalized_edit_similarity(ko_gold, ko_translated)
        trans_chrf = chrf_score(ko_gold, ko_translated)

        # 3. Braille accuracy (KR braille vs gold KR braille)
        braille_sim = normalized_edit_similarity(ko_gold_braille, ko_braille)

        results.append({
            'id': sid,
            'category': cat,
            'en_text': en_text,
            'ko_gold': ko_gold,
            'ko_translated': ko_translated,
            'decode_sim': round(decode_sim, 4),
            'trans_sim': round(trans_sim, 4),
            'trans_chrf': round(trans_chrf, 4),
            'braille_sim': round(braille_sim, 4),
        })

        status = 'OK' if decode_sim >= 0.99 else 'XX'
        print(f"  [{status}] {sid} {cat:<8} decode={decode_sim:.2f} trans={trans_sim:.2f} braille={braille_sim:.2f}")

    return results


def print_summary(results):
    from collections import defaultdict

    print(f"\n{'='*70}")
    print(f"  E2E Golden Set Results ({len(results)} sentences)")
    print(f"{'='*70}")

    # Per category
    by_cat = defaultdict(list)
    for r in results:
        by_cat[r['category']].append(r)

    print(f"\n  {'Category':<12} {'N':>4} {'Decode':>8} {'TransSim':>10} {'TransChrF':>10} {'BrailleSim':>11}")
    print(f"  {'-'*57}")

    for cat, rows in sorted(by_cat.items()):
        n = len(rows)
        avg_dec = sum(r['decode_sim'] for r in rows) / n
        avg_trans = sum(r['trans_sim'] for r in rows) / n
        avg_chrf = sum(r['trans_chrf'] for r in rows) / n
        avg_brl = sum(r['braille_sim'] for r in rows) / n
        print(f"  {cat:<12} {n:>4} {avg_dec:>8.4f} {avg_trans:>10.4f} {avg_chrf:>10.4f} {avg_brl:>11.4f}")

    # Overall
    n = len(results)
    print(f"  {'-'*57}")
    print(f"  {'OVERALL':<12} {n:>4} "
          f"{sum(r['decode_sim'] for r in results)/n:>8.4f} "
          f"{sum(r['trans_sim'] for r in results)/n:>10.4f} "
          f"{sum(r['trans_chrf'] for r in results)/n:>10.4f} "
          f"{sum(r['braille_sim'] for r in results)/n:>11.4f}")

    # Save results CSV
    out_path = PROJECT_ROOT / 'results' / 'e2e_golden_results.csv'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=[
            'id', 'category', 'decode_sim', 'trans_sim', 'trans_chrf', 'braille_sim'
        ])
        w.writeheader()
        for r in results:
            w.writerow({k: r[k] for k in w.fieldnames})
    print(f"\n  Results saved to {out_path}")


if __name__ == '__main__':
    results = run_e2e_test()
    print_summary(results)

"""
Shared round-trip harness for English and Korean golden-set checks.

This module keeps language-specific decode paths explicit so that:
- English round-trip uses the generic English braille decoder.
- Korean round-trip uses the dedicated Korean braille decoder.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from eval.similarity import chrf_score, normalized_edit_similarity
from pipeline.decoder import braille_to_text
from pipeline.encoder import encode_text_to_braille
from pipeline.ko_braille import encode_korean_braille
from pipeline.ko_braille_decoder import decode_korean_braille


# 제38항 [다만] — 숫자 뒤에 오는 'ㄴ, ㄷ, ㅁ, ㅋ, ㅌ, ㅍ, ㅎ'의 첫소리와 '운'의
# 약자는 숫자와 같은 칸이라 한 칸 띄어 적는다. 그 칸은 점자에만 있으므로 왕복
# 비교에서는 양쪽 모두 걷어내고 견준다.
_DIGIT_GAP = re.compile(r'(?<=\d) (?=[가-힣])')


def drop_digit_gap(text: str) -> str:
    return _DIGIT_GAP.sub('', text)


@dataclass(frozen=True)
class RoundtripSuite:
    lang: str
    suite_name: str
    decoder_name: str
    csv_filename: str


SUITES: dict[str, RoundtripSuite] = {
    'en': RoundtripSuite(
        lang='en',
        suite_name='english_roundtrip',
        decoder_name='pipeline.decoder.braille_to_text',
        csv_filename='golden_braille_roundtrip_en.csv',
    ),
    'ko': RoundtripSuite(
        lang='ko',
        suite_name='korean_roundtrip',
        decoder_name='pipeline.ko_braille_decoder.decode_korean_braille',
        csv_filename='golden_braille_roundtrip_ko.csv',
    ),
}


def resolve_suite(lang: str) -> RoundtripSuite:
    if lang not in SUITES:
        raise ValueError(f'Unsupported round-trip suite: {lang}')
    return SUITES[lang]


def encode_braille(text: str, lang: str) -> str:
    if lang == 'ko':
        return encode_korean_braille(text)
    return encode_text_to_braille(text)


def decode_braille(braille: str, lang: str) -> str:
    if lang == 'ko':
        return decode_korean_braille(braille)
    return braille_to_text(braille, lang='en')


def run_roundtrip_suite(
    lang: str,
    *,
    data_dir: Path,
    strip_whitespace: bool = False,
    strip_punctuation: bool = False,
) -> list[dict]:
    suite = resolve_suite(lang)
    csv_path = data_dir / suite.csv_filename
    results: list[dict] = []

    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = row['source_text']
            braille = encode_braille(source, lang=lang)
            roundtrip = decode_braille(braille, lang=lang)
            sim_edit = normalized_edit_similarity(
                source,
                roundtrip,
                strip_whitespace=strip_whitespace,
                strip_punctuation=strip_punctuation,
            )
            sim_chrf = chrf_score(source, roundtrip)

            results.append({
                'lang': lang,
                'suite': suite.suite_name,
                'decoder': suite.decoder_name,
                'id': row['id'],
                'category': row['category'],
                'source_text': source,
                'braille': braille,
                'roundtrip_text': roundtrip,
                'sim_edit': sim_edit,
                'sim_chrf': sim_chrf,
            })

    return results


def compute_category_stats(results: list[dict]) -> dict[str, dict]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in results:
        buckets[row['category']].append(row)

    stats: dict[str, dict] = {}
    for category, rows in sorted(buckets.items()):
        count = len(rows)
        stats[category] = {
            'count': count,
            'avg_sim_edit': sum(row['sim_edit'] for row in rows) / count,
            'avg_sim_chrf': sum(row['sim_chrf'] for row in rows) / count,
        }
    return stats


def compute_overall_stats(results: list[dict]) -> dict[str, float]:
    count = len(results)
    return {
        'count': count,
        'avg_sim_edit': sum(row['sim_edit'] for row in results) / count,
        'avg_sim_chrf': sum(row['sim_chrf'] for row in results) / count,
    }


def print_results(results: list[dict], stats: dict[str, dict], lang: str) -> None:
    suite = resolve_suite(lang)
    overall = compute_overall_stats(results)

    print(f"\n{'=' * 78}")
    print(f"  {suite.suite_name} [{lang.upper()}]  ({len(results)} sentences)")
    print(f"  decoder path: {suite.decoder_name}")
    print(f"{'=' * 78}")

    print(f"\n{'ID':<10} {'Category':<12} {'Edit Sim':>10} {'ChrF':>10}  Source (truncated)")
    print('-' * 78)
    for row in results:
        source = row['source_text']
        source_preview = source[:35] + ('...' if len(source) > 35 else '')
        print(
            f"{row['id']:<10} {row['category']:<12} "
            f"{row['sim_edit']:>10.4f} {row['sim_chrf']:>10.4f}  {source_preview}"
        )

    print(f"\n{'Category':<15} {'Count':>6} {'Avg Edit':>10} {'Avg ChrF':>10}")
    print('-' * 47)
    for category, category_stats in stats.items():
        print(
            f"{category:<15} {category_stats['count']:>6} "
            f"{category_stats['avg_sim_edit']:>10.4f} "
            f"{category_stats['avg_sim_chrf']:>10.4f}"
        )

    print('-' * 47)
    print(
        f"{'OVERALL':<15} {overall['count']:>6} "
        f"{overall['avg_sim_edit']:>10.4f} {overall['avg_sim_chrf']:>10.4f}"
    )


def save_results_csv(results: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                'lang',
                'suite',
                'decoder',
                'id',
                'category',
                'source_text',
                'roundtrip_text',
                'sim_edit',
                'sim_chrf',
            ],
        )
        writer.writeheader()
        for row in results:
            writer.writerow({
                'lang': row['lang'],
                'suite': row['suite'],
                'decoder': row['decoder'],
                'id': row['id'],
                'category': row['category'],
                'source_text': row['source_text'],
                'roundtrip_text': row['roundtrip_text'],
                'sim_edit': f"{row['sim_edit']:.6f}",
                'sim_chrf': f"{row['sim_chrf']:.6f}",
            })

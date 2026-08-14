"""Sort the round-trip mismatches that are left into 규정상 모호 / 구현 버그.

한국 점자는 63개 칸에 자모·약자·숫자·로마자·문장 부호를 모두 담는다. 그래서 한
칸이 여럿에 겹친다 — ⠲은 마침표이자 종성 ㅍ이자 로마자 종료표이고, ⠐은 쉼표이자
첫소리 ㄹ이다. 점자를 원문으로 되돌릴 때 이 자리들은 어느 쪽으로 읽어도 다른 쪽이
틀린다. 사람 독자는 문맥으로 읽지만 기계는 갈리지 않는다.

따라서 왕복 불일치는 두 가지가 섞여 있다.

  A. 규정상 모호 — 겹친 칸 때문에 생기는 것. 고칠 수 없고, 고치려 들면 다른 쪽이
     깨진다. 목록으로 확정해 두고 더 건드리지 않는다.
  B. 구현 버그 — 겹치지 않은 자리에서 잘못 읽은 것. 이것만 고친다.

Usage:
    python tests/ko_decoder_residual_classify.py
    python tests/ko_decoder_residual_classify.py --corpus results/foo.csv
"""

from __future__ import annotations

import argparse
import csv
import difflib
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

csv.field_size_limit(10_000_000)

from pipeline.ko_braille import encode_korean_braille  # noqa: E402
from pipeline.ko_braille_decoder import decode_korean_braille  # noqa: E402
from tests.roundtrip_harness import drop_digit_gap  # noqa: E402

DEFAULT_CORPORA = [
    PROJECT_ROOT / 'results' / 'ko_decoder_realtext_v11b_300.csv',
    PROJECT_ROOT / 'results' / 'ko_decoder_realtext_spotcheck_large.csv',
]
DEFAULT_OUTPUT = PROJECT_ROOT / 'results' / 'ko_decoder_residual_classes.csv'

LATIN = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
DIGITS = set('0123456789')
NUMBER_CONNECTORS = set('-.:,')
UNIMPLEMENTED_MARKS = set('/%~·「」『』*°℃…')

CLASSES = {
    'A1': '마침표와 로마자 종료표가 같은 칸 (제30항 해설)',
    'A2': '제38항 [다만] 이 넣는 빈칸 — 점자에만 있고 원문에는 없다',
    'A3': '붙임표·소수점으로 이어진 수 다음의 첫소리 글자가 숫자와 같은 칸 (제38항)',
    'A4': '종료표를 적지 않는 로마자 구간(제33~35항)의 경계',
    'A5': '아직 점형을 넣지 않은 부호가 그대로 흘러간 자리',
    'A6': '쉼표와 첫소리 ㄹ이 같은 칸 (제47항은 쉼표 뒤를 띄우게 하지만 원문이 붙여 썼다)',
    'B': '구현 버그 — 겹치지 않은 자리에서 잘못 읽었다',
}


def classify(src: str, got: str, i1: int, i2: int, j1: int, j2: int) -> str:
    lost, gained = src[i1:i2], got[j1:j2]
    before = src[max(0, i1 - 2):i1]
    prev = before[-1] if before else ''

    if lost == '.' and not gained and prev in LATIN:
        return 'A1'
    if not lost and gained == '.' and prev in LATIN:
        return 'A1'
    if not lost and gained == ' ' and prev in DIGITS:
        return 'A2'
    if (prev in NUMBER_CONNECTORS or prev in DIGITS) and (
        any(c in DIGITS for c in lost) or any(c in DIGITS for c in gained)
    ):
        return 'A3'
    if any(c in LATIN for c in lost) != any(c in LATIN for c in gained):
        return 'A4'
    if any(c in UNIMPLEMENTED_MARKS for c in lost + gained):
        return 'A5'
    if lost.startswith(',') or gained.startswith(','):
        return 'A6'
    return 'B'


def main() -> None:
    parser = argparse.ArgumentParser(description='Residual round-trip mismatch classifier')
    parser.add_argument('--corpus', action='append', help='CSV with a "source" column')
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    corpora = [Path(c) for c in args.corpus] if args.corpus else DEFAULT_CORPORA
    rows: list[dict] = []
    counts: Counter[str] = Counter()
    checked = failed = 0

    for path in corpora:
        if not path.exists():
            continue
        for row in csv.DictReader(path.open(encoding='utf-8')):
            source = row.get('source') or ''
            if not source:
                continue
            checked += 1
            roundtrip = decode_korean_braille(encode_korean_braille(source))
            if drop_digit_gap(roundtrip) == drop_digit_gap(source):
                continue
            failed += 1
            matcher = difflib.SequenceMatcher(None, source, roundtrip, autojunk=False)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    continue
                kind = classify(source, roundtrip, i1, i2, j1, j2)
                counts[kind] += 1
                rows.append({
                    'corpus': path.name,
                    'class': kind,
                    'reason': CLASSES[kind],
                    'source_fragment': source[max(0, i1 - 24):i2 + 10],
                    'lost': source[i1:i2],
                    'gained': roundtrip[j1:j2],
                })

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f, fieldnames=['corpus', 'class', 'reason', 'source_fragment', 'lost', 'gained']
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f'rows={checked} mismatched_rows={failed} diffs={sum(counts.values())} output={output}')
    for kind in sorted(CLASSES):
        if counts[kind]:
            print(f'  {kind}  {counts[kind]:4d}  {CLASSES[kind]}')
    bugs = counts['B']
    print(f'\n규정상 모호 {sum(counts.values()) - bugs}건, 구현 버그 {bugs}건')
    raise SystemExit(1 if bugs else 0)


if __name__ == '__main__':
    main()

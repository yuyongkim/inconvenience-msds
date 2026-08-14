"""
Korean Braille Rule Checker

Checks automated rules against Korean braille output (Unicode braille characters).
Returns violation counts per rule, normalized as violations per 1,000 braille cells.

Rules implemented:
  1. number_indicator   - 수표(⠼)로 열린 수의 구조 (제37·39·49항)
  2. bracket_pairing    - 2017 개정 괄호 두 칸 표기의 짝 (제54~56항)
  3. capital_indicator   - Capital letter indicator usage (⠠) check
  4. space_around_dash  - Proper spacing around dashes/hyphens
  5. consecutive_spaces - No excessive consecutive spaces (>2)

Korean braille Unicode range: U+2800 to U+28FF
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from pipeline.ko_braille import KO_PUNCT_BRAILLE


# ---------------------------------------------------------------------------
# Braille constants (Unicode)
# ---------------------------------------------------------------------------

BRAILLE_BLOCK_START = 0x2800
BRAILLE_BLOCK_END = 0x28FF

# Korean braille number indicator
NUMBER_INDICATOR = '\u283C'  # ⠼ (dots 3-4-5-6)

# Braille digit patterns (after number indicator): 1-0 mapped to braille
BRAILLE_DIGITS = {
    '\u2801': '1',  # ⠁ dot 1
    '\u2803': '2',  # ⠃ dots 1-2
    '\u2809': '3',  # ⠉ dots 1-4
    '\u2819': '4',  # ⠙ dots 1-4-5
    '\u2811': '5',  # ⠑ dots 1-5
    '\u280B': '6',  # ⠋ dots 1-2-4
    '\u281B': '7',  # ⠛ dots 1-2-4-5
    '\u2813': '8',  # ⠓ dots 1-2-5
    '\u280A': '9',  # ⠊ dots 2-4
    '\u281A': '0',  # ⠚ dots 2-4-5
}

# Capital indicator
CAPITAL_INDICATOR = '\u2820'  # ⠠ (dot 6)

# 괄호는 2017 개정에서 두 칸이 되었다(제54~56항). 한 칸짜리 점형으로는 종성·부호와
# 구분되지 않으므로 짝을 셀 수 없다.
BRACKET_PAIRS = {
    KO_PUNCT_BRAILLE['(']: KO_PUNCT_BRAILLE[')'],
    KO_PUNCT_BRAILLE['{']: KO_PUNCT_BRAILLE['}'],
    KO_PUNCT_BRAILLE['[']: KO_PUNCT_BRAILLE[']'],
}

# Braille space
BRAILLE_SPACE = '\u2800'  # ⠀ (empty cell, often used as space)


def is_braille_cell(ch: str) -> bool:
    """Check if a character is a braille Unicode cell."""
    return BRAILLE_BLOCK_START <= ord(ch) <= BRAILLE_BLOCK_END


def count_braille_cells(text: str) -> int:
    """Count the number of braille cells in text."""
    return sum(1 for ch in text if is_braille_cell(ch))


# ---------------------------------------------------------------------------
# Rule check functions
# ---------------------------------------------------------------------------

@dataclass
class RuleViolation:
    rule: str
    position: int
    description: str


@dataclass
class RuleCheckResult:
    rule: str
    violations: list[RuleViolation] = field(default_factory=list)
    total_cells: int = 0

    @property
    def count(self) -> int:
        return len(self.violations)

    @property
    def rate_per_1000(self) -> float:
        if self.total_cells == 0:
            return 0.0
        return (self.count / self.total_cells) * 1000


def check_number_indicator(text: str) -> RuleCheckResult:
    """
    Rule 1: 수는 수표(⠼)를 앞세워 적는다 (제37항).

    숫자 점형은 로마자 a–j와 같고, 첫소리 'ㄴ, ㄷ, ㅁ, ㅋ, ㅌ, ㅍ, ㅎ'이나 'ㅏ' 약자와도
    같은 칸이다. 그래서 "수표 없는 숫자 칸"을 세면 한글을 전부 위반으로 잡는다.
    대신 수표가 연 구간의 구조만 본다.

      - 수표 뒤에는 숫자가 와야 한다
      - 이미 수 안인데 수표를 다시 적으면 안 된다 (제39·49항)
    """
    result = RuleCheckResult(rule='number_indicator', total_cells=count_braille_cells(text))
    digit_set = set(BRAILLE_DIGITS.keys())
    # 제39·49항 — 수를 끊지 않고 이어 주는 부호
    connectors = {'\u2824', '\u2832', '\u2810', '\u2810\u2802'}

    in_number = False
    for i, ch in enumerate(text):
        if ch == NUMBER_INDICATOR:
            nxt = text[i + 1] if i + 1 < len(text) else ''
            if nxt not in digit_set:
                result.violations.append(RuleViolation(
                    rule='number_indicator',
                    position=i,
                    description=f'Number indicator at pos {i} not followed by a digit',
                ))
            elif in_number:
                result.violations.append(RuleViolation(
                    rule='number_indicator',
                    position=i,
                    description=f'Number indicator repeated inside a number at pos {i}',
                ))
            in_number = True
            continue
        if ch in digit_set or ch in connectors:
            continue
        in_number = False
    return result


def check_bracket_pairing(text: str) -> RuleCheckResult:
    """
    Rule 2: Opening brackets/quotes must have matching closing counterparts.
    Works on both braille and plain-text bracket characters.
    """
    result = RuleCheckResult(rule='bracket_pairing', total_cells=count_braille_cells(text))

    for open_seq, close_seq in BRACKET_PAIRS.items():
        depth = 0
        i = 0
        while i < len(text):
            if text.startswith(open_seq, i):
                depth += 1
                i += len(open_seq)
                continue
            if text.startswith(close_seq, i):
                depth -= 1
                if depth < 0:
                    result.violations.append(RuleViolation(
                        rule='bracket_pairing',
                        position=i,
                        description=f'Unmatched closing bracket at pos {i}',
                    ))
                    depth = 0
                i += len(close_seq)
                continue
            i += 1
        if depth > 0:
            result.violations.append(RuleViolation(
                rule='bracket_pairing',
                position=-1,
                description=f'{depth} unclosed bracket(s)',
            ))
    return result


def check_capital_indicator(text: str) -> RuleCheckResult:
    """
    Rule 3: Capital letter indicator (⠠) should be followed by a letter cell,
    not by space or another indicator.
    """
    result = RuleCheckResult(rule='capital_indicator', total_cells=count_braille_cells(text))

    for i, ch in enumerate(text):
        if ch == CAPITAL_INDICATOR:
            if i + 1 >= len(text):
                result.violations.append(RuleViolation(
                    rule='capital_indicator',
                    position=i,
                    description=f'Capital indicator at end of text (pos {i})'
                ))
            elif text[i + 1] in (' ', BRAILLE_SPACE, '\n', '\t'):
                result.violations.append(RuleViolation(
                    rule='capital_indicator',
                    position=i,
                    description=f'Capital indicator followed by space at pos {i}'
                ))
    return result


def check_space_around_dash(text: str) -> RuleCheckResult:
    """
    Rule 4: Dashes (⠤⠤ or plain --) should have proper spacing.
    In Korean braille, long dashes typically need spaces on both sides.
    """
    result = RuleCheckResult(rule='space_around_dash', total_cells=count_braille_cells(text))

    # Braille dash: ⠤ (dots 3-6) doubled = ⠤⠤
    dash_pattern = '\u2824\u2824'
    idx = 0
    while True:
        pos = text.find(dash_pattern, idx)
        if pos == -1:
            break
        # Check space before
        if pos > 0 and text[pos - 1] not in (' ', BRAILLE_SPACE, '\n'):
            result.violations.append(RuleViolation(
                rule='space_around_dash',
                position=pos,
                description=f'No space before dash at pos {pos}'
            ))
        # Check space after
        end = pos + len(dash_pattern)
        if end < len(text) and text[end] not in (' ', BRAILLE_SPACE, '\n'):
            result.violations.append(RuleViolation(
                rule='space_around_dash',
                position=pos,
                description=f'No space after dash at pos {pos}'
            ))
        idx = end
    return result


def check_consecutive_spaces(text: str) -> RuleCheckResult:
    """
    Rule 5: No more than 2 consecutive spaces (or braille empty cells).
    Excessive whitespace is typically a formatting error.
    """
    result = RuleCheckResult(rule='consecutive_spaces', total_cells=count_braille_cells(text))

    space_chars = {' ', BRAILLE_SPACE}
    run_start = None
    run_len = 0

    for i, ch in enumerate(text):
        if ch in space_chars:
            if run_start is None:
                run_start = i
                run_len = 1
            else:
                run_len += 1
        else:
            if run_len > 2:
                result.violations.append(RuleViolation(
                    rule='consecutive_spaces',
                    position=run_start,
                    description=f'{run_len} consecutive spaces starting at pos {run_start}'
                ))
            run_start = None
            run_len = 0

    if run_len > 2:
        result.violations.append(RuleViolation(
            rule='consecutive_spaces',
            position=run_start,
            description=f'{run_len} consecutive spaces starting at pos {run_start}'
        ))

    return result


# ---------------------------------------------------------------------------
# Aggregate check
# ---------------------------------------------------------------------------

ALL_RULES = [
    check_number_indicator,
    check_bracket_pairing,
    check_capital_indicator,
    check_space_around_dash,
    check_consecutive_spaces,
]


def check_all_rules(text: str) -> dict:
    """
    Run all rule checks on a braille text.

    Returns:
        dict with keys:
          - 'results': list of RuleCheckResult
          - 'total_violations': int
          - 'total_cells': int
          - 'violation_rate_per_1000': float
    """
    total_cells = count_braille_cells(text)
    # If no braille cells, also count regular characters as a fallback
    if total_cells == 0:
        total_cells = len(text.replace(' ', '').replace('\n', ''))

    results = []
    total_violations = 0
    for fn in ALL_RULES:
        r = fn(text)
        r.total_cells = total_cells  # normalize to same total
        results.append(r)
        total_violations += r.count

    rate = (total_violations / total_cells * 1000) if total_cells > 0 else 0.0

    return {
        'results': results,
        'total_violations': total_violations,
        'total_cells': total_cells,
        'violation_rate_per_1000': rate,
    }


if __name__ == '__main__':
    # Quick demo
    sample = '⠠⠓⠑⠇⠇⠕ ⠼⠁⠃⠉ (⠞⠑⠎⠞'
    report = check_all_rules(sample)
    print(f"Total cells: {report['total_cells']}")
    print(f"Total violations: {report['total_violations']}")
    print(f"Rate per 1000: {report['violation_rate_per_1000']:.1f}")
    for r in report['results']:
        print(f"  {r.rule}: {r.count} violations ({r.rate_per_1000:.1f}/1000)")
        for v in r.violations:
            print(f"    - {v.description}")

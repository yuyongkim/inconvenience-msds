"""
Document structure extractor.

Analyzes braille lines to identify document blocks:
  P = Paragraph
  L = List (ordered/unordered)
  T = Table
  M = Math

Input: list of braille lines (raw strings)
Output: list of block dicts with type and line range
"""

from __future__ import annotations
import re


def extract_structure(lines: list[str]) -> list[dict]:
    """
    Extract document structure blocks from braille lines.

    Args:
        lines: List of raw braille lines (0-indexed internally, 1-based in output)

    Returns:
        List of block dicts:
        [
            {"block_id": "b1", "type": "P", "start_line": 1, "end_line": 3},
            {"block_id": "b2", "type": "L", "start_line": 5, "end_line": 8},
            ...
        ]
    """
    if not lines:
        return []

    # Classify each line
    line_types = []
    for line in lines:
        line_types.append(_classify_line(line))

    # Group consecutive same-type lines into blocks
    blocks = []
    block_counter = 1
    current_type = None
    start = None

    for i, ltype in enumerate(line_types):
        if ltype == 'empty':
            # End current block if any
            if current_type is not None:
                blocks.append(_make_block(block_counter, current_type, start, i - 1))
                block_counter += 1
                current_type = None
                start = None
            continue

        if current_type is None:
            # Start new block
            current_type = ltype
            start = i
        elif ltype == current_type:
            # Continue current block
            continue
        elif ltype == 'text' and current_type in ('P', 'text'):
            # Continuation of paragraph
            current_type = 'P'
            continue
        else:
            # Type changed — close current, start new
            blocks.append(_make_block(block_counter, current_type, start, i - 1))
            block_counter += 1
            current_type = ltype
            start = i

    # Close last block
    if current_type is not None:
        blocks.append(_make_block(block_counter, current_type, start, len(lines) - 1))

    return blocks


def _classify_line(line: str) -> str:
    """Classify a single line by its structural role."""
    stripped = line.strip()

    if not stripped:
        return 'empty'

    # Ordered list: starts with digit(s) + . or ) + space
    if re.match(r'^\d+[.)]\s', stripped):
        return 'L'

    # Unordered list: starts with - or * + space
    if re.match(r'^[-*+]\s', stripped):
        return 'L'

    # BRF list marker: starts with # (number indicator) + letter + . (period)
    if re.match(r'^#[a-j]\.\s', stripped, re.IGNORECASE):
        return 'L'

    # Table: contains multiple tabs or pipe characters
    if stripped.count('\t') >= 2 or stripped.count('|') >= 2:
        return 'T'

    # Math: contains math-related patterns
    if _looks_like_math(stripped):
        return 'M'

    # Default: paragraph text
    return 'P'


def _looks_like_math(line: str) -> bool:
    """Heuristic check for math content."""
    math_patterns = [
        r'[=+\-*/^]\s*\d',        # operators with numbers
        r'\d\s*[=+\-*/^]',        # numbers with operators
        r'[xyz]\s*[=^]',          # variable assignments
        r'f\([xyz]\)',             # function notation
        r'\\frac|\\sum|\\int',    # LaTeX commands
        r'\bsin\b|\bcos\b|\btan\b',  # trig functions
        r'\bsqrt\b|\blog\b|\bln\b',  # math functions
    ]
    math_count = sum(1 for p in math_patterns if re.search(p, line, re.IGNORECASE))
    # Need at least 2 indicators to classify as math (avoid false positives)
    return math_count >= 2


def _make_block(counter: int, block_type: str, start: int, end: int) -> dict:
    """Create a block dict with 1-based line numbers."""
    # Normalize type
    if block_type == 'text':
        block_type = 'P'

    return {
        'block_id': f'b{counter}',
        'type': block_type,
        'start_line': start + 1,  # 1-based
        'end_line': end + 1,      # 1-based
    }

"""
Text-to-Braille encoder (점역).

Converts English plain text to Unicode braille (UEB-like).
Used primarily for generating test braille files from golden set sentences.

This is a simplified UEB encoder — sufficient for test data generation,
not a full UEB Grade 2 implementation (contractions are not applied).
"""

from __future__ import annotations
from pipeline.brf_tables import (
    ASCII_TO_BRAILLE, DIGIT_TO_LETTER,
    NUMBER_INDICATOR_BRAILLE, CAPITAL_INDICATOR_BRAILLE,
)

# UEB punctuation: text character -> braille Unicode
# These are the "proper" UEB representations (may differ from BRF ASCII mapping)
UEB_PUNCTUATION = {
    '.': '\u2832',  # ⠲ dots 2-5-6   period
    ',': '\u2820',  # ⠠ dot 6        comma  (same as capital indicator in BRF)
    '?': '\u2839',  # ⠹ dots 1-4-5-6 question mark
    '!': '\u2816',  # ⠖ dots 2-3-5   exclamation mark
    ':': '\u2812',  # ⠒ dots 2-5     colon
    ';': '\u2830',  # ⠰ dots 5-6     semicolon (UEB: dots 2-3)
    '-': '\u2824',  # ⠤ dots 3-6     hyphen
    "'": '\u2804',  # ⠄ dot 3        apostrophe
    '"': '\u2826',  # ⠦ dots 2-3-6   opening quote (simplified)
    '(': '\u2837',  # ⠷ dots 1-2-3-5-6 opening paren
    ')': '\u283E',  # ⠾ dots 2-3-4-5-6 closing paren
    '/': '\u280C',  # ⠌ dots 3-4     slash
    '+': '\u282C',  # ⠬ dots 3-4-6   plus
    '=': '\u2836\u2836',  # ⠶⠶ equals (two-cell to avoid conflict with ?)
    '*': '\u2821',  # ⠡ dots 1-6     asterisk
    '@': '\u2808',  # ⠈ dot 4        at sign
    '$': '\u282B',  # ⠫ dots 1-2-4-6 dollar sign
    '%': '\u2829',  # ⠩ dots 1-4-6   percent sign
}

# Letter -> braille cell (lowercase only)
LETTER_TO_BRAILLE = {}
for ch in 'abcdefghijklmnopqrstuvwxyz':
    if ch in ASCII_TO_BRAILLE:
        LETTER_TO_BRAILLE[ch] = ASCII_TO_BRAILLE[ch]


def encode_text_to_braille(text: str) -> str:
    """
    Encode English plain text to Unicode braille string.

    Handles:
      - Lowercase/uppercase letters (capital indicator + letter)
      - Digits (number indicator + letter-mapped-to-digit)
      - Basic punctuation
      - Spaces preserved as braille space (U+2800)

    Does NOT handle:
      - UEB Grade 2 contractions
      - Multi-cell symbols (em dash, etc.)
      - Typeform indicators (bold, italic)

    Args:
        text: English plain text

    Returns:
        Unicode braille string
    """
    result = []
    i = 0
    in_number = False

    while i < len(text):
        ch = text[i]

        # Space
        if ch == ' ':
            result.append('\u2800')  # braille space
            in_number = False
            i += 1
            continue

        # Newline
        if ch == '\n':
            result.append('\n')
            in_number = False
            i += 1
            continue

        # Digit
        if ch.isdigit():
            if not in_number:
                result.append(NUMBER_INDICATOR_BRAILLE)  # ⠼
                in_number = True
            # Map digit to letter braille cell
            letter = DIGIT_TO_LETTER.get(ch, 'a')
            result.append(LETTER_TO_BRAILLE.get(letter, '\u2800'))
            i += 1
            continue

        # Decimal point inside number (e.g., 3.14)
        if ch == '.' and in_number and i + 1 < len(text) and text[i + 1].isdigit():
            result.append('\u2832')  # ⠲ UEB decimal point / period
            i += 1
            continue

        # Letter
        if ch.isalpha():
            if in_number:
                # Insert letter indicator to terminate number mode
                result.append('\u2830')  # ⠰ dots 5-6 = grade 1 / letter indicator
                in_number = False
            if ch.isupper():
                result.append(CAPITAL_INDICATOR_BRAILLE)  # ⠠
                lower = ch.lower()
            else:
                lower = ch
            braille = LETTER_TO_BRAILLE.get(lower)
            if braille:
                result.append(braille)
            else:
                result.append('\u2800')  # fallback: empty cell
            i += 1
            continue

        # Punctuation
        in_number = False
        braille = UEB_PUNCTUATION.get(ch)
        if braille:
            result.append(braille)
        else:
            # Unknown character: skip or insert empty cell
            result.append('\u2800')
        i += 1

    return ''.join(result)


def encode_document(text: str, lines_per_page: int = 25) -> str:
    """
    Encode a multi-line text document to braille with page breaks.

    Args:
        text: Full document text
        lines_per_page: Lines per page (0 = no page breaks)

    Returns:
        Unicode braille string with page break markers
    """
    braille = encode_text_to_braille(text)
    if lines_per_page <= 0:
        return braille

    lines = braille.split('\n')
    pages = []
    for i in range(0, len(lines), lines_per_page):
        page_lines = lines[i:i + lines_per_page]
        pages.append('\n'.join(page_lines))

    return '\n=== PAGE BREAK ===\n'.join(pages)


if __name__ == '__main__':
    # Quick demo
    samples = [
        "This is a simple sentence.",
        "The meeting starts at 3:45 p.m.",
        "If x squared equals 4, then x is 2.",
        "Step 1: Open the valve. Step 2: Check pressure.",
    ]
    for s in samples:
        b = encode_text_to_braille(s)
        print(f"Text:    {s}")
        print(f"Braille: {b}")
        print()

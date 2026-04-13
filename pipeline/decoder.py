"""
Braille-to-text decoder (역점역).

Converts braille strings (BRF ASCII or Unicode) to English plain text.
v1: Context-aware UEB decoding with letter/number/punctuation support.

Key challenge: ⠠ (dot 6) is both capital indicator AND comma in UEB.
Disambiguation: if followed by a letter cell → capital; otherwise → comma.
"""

from __future__ import annotations
from pipeline.brf_tables import (
    ASCII_TO_BRAILLE, BRAILLE_TO_ASCII,
    LETTER_TO_DIGIT, DIGIT_TO_LETTER,
    NUMBER_INDICATOR_BRAILLE, CAPITAL_INDICATOR_BRAILLE,
)


def _is_braille(ch: str) -> bool:
    return 0x2800 <= ord(ch) <= 0x28FF


# Build a set of braille cells that represent letters (a-z)
_LETTER_CELLS = set()
for c in 'abcdefghijklmnopqrstuvwxyz':
    if c in ASCII_TO_BRAILLE:
        _LETTER_CELLS.add(ASCII_TO_BRAILLE[c])

# Braille cells that map to digits (same cells as a-j, but after number indicator)
_DIGIT_CELLS = {}
for letter, digit in LETTER_TO_DIGIT.items():
    if letter in ASCII_TO_BRAILLE:
        _DIGIT_CELLS[ASCII_TO_BRAILLE[letter]] = digit

# Direct punctuation mapping: braille cell -> text character
# These are unambiguous (not context-dependent)
_PUNCT_MAP = {
    '\u2832': '.',   # ⠲ period
    '\u2812': ':',   # ⠒ colon
    '\u2816': '!',   # ⠖ exclamation
    # '\u2836': handled in context (⠶⠶ = equals, lone ⠶ = question mark)
    '\u2837': '(',   # ⠷ opening paren
    '\u283E': ')',   # ⠾ closing paren
    '\u2824': '-',   # ⠤ hyphen
    '\u2804': "'",   # ⠄ apostrophe
    '\u2826': '"',   # ⠦ opening quote
    '\u2834': '"',   # ⠴ closing quote
    '\u280C': '/',   # ⠌ slash
    '\u282C': '+',   # ⠬ plus
    '\u2821': '*',   # ⠡ asterisk
    '\u282B': '$',   # ⠫ dollar sign
    '\u2829': '%',   # ⠩ percent sign
    '\u2808': '@',   # ⠈ at sign
    '\u2830': ';',   # ⠰ semicolon
    '\u2828': '.',   # ⠨ BRF period (dots 4-6)
    '\u2831': ':',   # ⠱ BRF colon (dots 1-5-6)
    '\u282E': '!',   # ⠮ BRF exclamation
    '\u2839': '?',   # ⠹ BRF question
}

BRAILLE_SPACE = '\u2800'


def decode_unicode_braille(braille_str: str) -> str:
    """
    Decode Unicode braille string to English text with context awareness.
    """
    result = []
    i = 0
    chars = list(braille_str)
    n = len(chars)
    in_number = False

    while i < n:
        ch = chars[i]

        # Non-braille passthrough (regular space, newline, etc.)
        if not _is_braille(ch):
            if ch == ' ':
                result.append(' ')
                in_number = False
            else:
                result.append(ch)
                if ch == '\n':
                    in_number = False
            i += 1
            continue

        # Braille space
        if ch == BRAILLE_SPACE:
            result.append(' ')
            in_number = False
            i += 1
            continue

        # Number indicator ⠼
        if ch == NUMBER_INDICATOR_BRAILLE:
            in_number = True
            i += 1
            continue

        # Capital indicator / comma ⠠ — context-dependent
        if ch == CAPITAL_INDICATOR_BRAILLE:
            # Look ahead: if next char is a letter cell → capital
            if i + 1 < n and chars[i + 1] in _LETTER_CELLS:
                # Capitalize the next letter
                next_cell = chars[i + 1]
                ascii_ch = BRAILLE_TO_ASCII.get(next_cell, '?')
                result.append(ascii_ch.upper())
                in_number = False
                i += 2
                continue
            else:
                # It's a comma
                result.append(',')
                in_number = False
                i += 1
                continue

        # In number mode: letter cells → digits
        if in_number and ch in _DIGIT_CELLS:
            result.append(_DIGIT_CELLS[ch])
            i += 1
            continue

        # Period/decimal in number mode
        if in_number and ch == '\u2832':  # ⠲
            # Check if followed by another digit cell → decimal point
            if i + 1 < n and chars[i + 1] in _DIGIT_CELLS:
                result.append('.')
            else:
                result.append('.')
                in_number = False
            i += 1
            continue

        # Letter indicator ⠰ (dots 5-6) — terminates number mode
        if ch == '\u2830' and in_number:
            in_number = False
            i += 1
            continue

        # Non-digit in number mode → exit number mode
        if in_number and ch not in _DIGIT_CELLS:
            in_number = False

        # ⠶ context: ⠶⠶ = equals, lone ⠶ = question mark
        if ch == '\u2836':
            if i + 1 < n and chars[i + 1] == '\u2836':
                result.append('=')
                i += 2
                continue
            else:
                result.append('?')
                i += 1
                continue

        # Direct punctuation
        if ch in _PUNCT_MAP:
            result.append(_PUNCT_MAP[ch])
            i += 1
            continue

        # Letter cells
        if ch in _LETTER_CELLS:
            ascii_ch = BRAILLE_TO_ASCII.get(ch, '?')
            result.append(ascii_ch)
            i += 1
            continue

        # Unknown braille cell → try ASCII mapping, else '?'
        ascii_ch = BRAILLE_TO_ASCII.get(ch)
        if ascii_ch:
            result.append(ascii_ch)
        else:
            result.append('?')
        i += 1

    return ''.join(result)


def decode_brf_line(brf_line: str, grade: int = 2) -> str:
    """
    Decode a single BRF (ASCII) line to English text.
    Supports UEB Grade 1 and Grade 2 (contractions).
    """
    from pipeline.ueb_g2_tables import (
        ALPHABETIC_WORDSIGNS, STRONG_GROUPSIGNS_SAFE,
        STRONG_GROUPSIGNS_CONTEXTUAL, LOWER_GROUPSIGNS,
        MULTI_CHAR_CONTRACTIONS, SHORTFORMS, LOWER_WORDSIGNS,
    )

    result = []
    i = 0
    n = len(brf_line)
    in_number = False
    capitalize_next = False
    capitalize_word = False  # ,, = capitalize whole word

    def _at_word_boundary(pos: int) -> bool:
        """Check if position is at a word boundary (start or end)."""
        before_ok = (pos == 0 or brf_line[pos - 1] in ' \t-"\'(<alan alan')
        return before_ok

    # Characters that count as "part of a word" in BRF
    _WORD_CHARS = set('abcdefghijklmnopqrstuvwxyz&*<>+\\|[]$!/%()?12589}";.@~_\'')

    def _is_standalone(pos: int, length: int) -> bool:
        """Check if sequence at pos of given length is 'standing alone'."""
        before = pos == 0 or brf_line[pos - 1] not in _WORD_CHARS
        after = (pos + length >= n) or brf_line[pos + length] not in _WORD_CHARS
        return before and after

    while i < n:
        ch = brf_line[i]

        # Double capital indicator: ,, = capitalize entire word
        if ch == ',' and i + 1 < n and brf_line[i + 1] == ',':
            capitalize_word = True
            i += 2
            continue

        # Capital indicator: , + letter
        if ch == ',':
            capitalize_next = True
            i += 1
            continue

        # Number indicator
        if ch == '#':
            in_number = True
            i += 1
            continue

        # Number terminator (letter indicator ;)
        if ch == ';' and in_number:
            in_number = False
            i += 1
            continue

        # Digits in number mode
        if in_number and ch.lower() in LETTER_TO_DIGIT:
            result.append(LETTER_TO_DIGIT[ch.lower()])
            i += 1
            continue

        # Period in number mode (decimal point or period)
        if in_number and ch == '4':
            result.append('.')
            i += 1
            continue

        # Comma in number mode
        if in_number and ch == '1':
            result.append(',')
            i += 1
            continue

        # Hyphen/dash in number mode
        if in_number and ch == '-':
            result.append('-')
            in_number = False
            i += 1
            continue

        # Space exits number mode and capitalize_word mode
        if ch == ' ':
            in_number = False
            if capitalize_word:
                capitalize_word = False
            result.append(' ')
            i += 1
            continue

        # Exit number mode on non-digit-compatible char
        if in_number and ch not in 'abcdefghij':
            in_number = False

        # === Grade 2 contractions (only if grade >= 2) ===
        if grade >= 2:
            # Try multi-char contractions (longest match first)
            matched = False

            # 3-char sequences
            if i + 2 < n:
                seq3 = brf_line[i:i+3]
                if seq3 in MULTI_CHAR_CONTRACTIONS:
                    expanded = MULTI_CHAR_CONTRACTIONS[seq3]
                    if capitalize_next:
                        expanded = expanded[0].upper() + expanded[1:]
                        capitalize_next = False
                    if capitalize_word:
                        expanded = expanded.upper()
                    result.append(expanded)
                    i += 3
                    continue

            # 2-char sequences
            if i + 1 < n:
                seq2 = brf_line[i:i+2]
                if seq2 in MULTI_CHAR_CONTRACTIONS:
                    expanded = MULTI_CHAR_CONTRACTIONS[seq2]
                    if capitalize_next:
                        expanded = expanded[0].upper() + expanded[1:]
                        capitalize_next = False
                    if capitalize_word:
                        expanded = expanded.upper()
                    result.append(expanded)
                    i += 2
                    continue

            # Shortforms (whole word match)
            # Try longest possible shortform from current position
            for slen in range(6, 1, -1):
                if i + slen <= n:
                    candidate = brf_line[i:i+slen]
                    if candidate in SHORTFORMS and _is_standalone(i, slen):
                        expanded = SHORTFORMS[candidate]
                        if capitalize_next:
                            expanded = expanded[0].upper() + expanded[1:]
                            capitalize_next = False
                        if capitalize_word:
                            expanded = expanded.upper()
                        result.append(expanded)
                        i += slen
                        matched = True
                        break
            if matched:
                continue

            # Safe groupsigns (no punctuation conflict, always apply)
            if ch in STRONG_GROUPSIGNS_SAFE:
                expanded = STRONG_GROUPSIGNS_SAFE[ch]
                if capitalize_next:
                    expanded = expanded[0].upper() + expanded[1:]
                    capitalize_next = False
                if capitalize_word:
                    expanded = expanded.upper()
                result.append(expanded)
                i += 1
                continue

            # Contextual groupsigns (conflict with punct — only within words)
            def _in_word_context(pos):
                """Check if char at pos is adjacent to word-forming chars."""
                before = pos > 0 and brf_line[pos-1] in _WORD_CHARS
                after = pos + 1 < n and brf_line[pos+1] in _WORD_CHARS
                return before or after

            if ch in STRONG_GROUPSIGNS_CONTEXTUAL and _in_word_context(i):
                expanded = STRONG_GROUPSIGNS_CONTEXTUAL[ch]
                if capitalize_next:
                    expanded = expanded[0].upper() + expanded[1:]
                    capitalize_next = False
                if capitalize_word:
                    expanded = expanded.upper()
                result.append(expanded)
                i += 1
                continue

            # Lower groupsigns (be, en — within words only)
            if ch in LOWER_GROUPSIGNS and _in_word_context(i):
                expanded = LOWER_GROUPSIGNS[ch]
                if capitalize_next:
                    expanded = expanded[0].upper() + expanded[1:]
                    capitalize_next = False
                if capitalize_word:
                    expanded = expanded.upper()
                result.append(expanded)
                i += 1
                continue

            # Alphabetic wordsigns (single letter standalone = word)
            if ch.isalpha() and ch.lower() in ALPHABETIC_WORDSIGNS and _is_standalone(i, 1):
                expanded = ALPHABETIC_WORDSIGNS[ch.lower()]
                if capitalize_next or ch.isupper():
                    expanded = expanded[0].upper() + expanded[1:]
                    capitalize_next = False
                if capitalize_word:
                    expanded = expanded.upper()
                result.append(expanded)
                i += 1
                continue

            # Lower wordsigns (standalone)
            if ch in LOWER_WORDSIGNS and _is_standalone(i, 1):
                expanded = LOWER_WORDSIGNS[ch]
                if capitalize_next:
                    expanded = expanded[0].upper() + expanded[1:]
                    capitalize_next = False
                result.append(expanded)
                i += 1
                continue

        # === Punctuation ===
        PUNCT = {
            '4': '.', '1': ',', '2': ';', '6': '!', '8': ':', '3': "'",
            '0': '"', '7': '?',
            '?': '?',  # alternate
        }
        if ch in PUNCT:
            result.append(PUNCT[ch])
            i += 1
            continue

        # BRF formatting characters
        if ch == '_':
            # Italic/underline indicator — skip
            i += 1
            continue
        if ch == '~':
            # Bold indicator — skip
            i += 1
            continue

        # Regular letter
        if ch.isalpha():
            out_ch = ch
            if capitalize_next:
                out_ch = ch.upper()
                capitalize_next = False
            elif capitalize_word:
                out_ch = ch.upper()
            result.append(out_ch)
            i += 1
            continue

        # Pass through anything else
        if capitalize_next:
            capitalize_next = False
        result.append(ch)
        i += 1

    return ''.join(result)


def braille_to_text(braille_str: str, lang: str = 'en') -> str:
    """
    Main interface: convert braille string to plain text.
    Auto-detects Unicode braille vs BRF ASCII.
    """
    if not braille_str:
        return ''

    has_unicode = any(_is_braille(ch) for ch in braille_str)

    if has_unicode:
        return decode_unicode_braille(braille_str)
    else:
        lines = braille_str.splitlines()
        decoded = [decode_brf_line(line) for line in lines]
        return '\n'.join(decoded)

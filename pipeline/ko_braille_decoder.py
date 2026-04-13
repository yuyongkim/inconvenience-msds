"""
Korean Braille Decoder.

Reverse of ko_braille.py — converts Korean braille back to Korean text.
Used for round-trip validation (encode→decode should return original).
"""

from __future__ import annotations
from pipeline.ko_braille import (
    CHOSUNG_BRAILLE, JUNGSUNG_BRAILLE, JONGSUNG_BRAILLE,
    KO_NUMBER_INDICATOR, KO_DIGIT_BRAILLE, KO_PUNCT_BRAILLE,
    CHOSUNG_LIST, JUNGSUNG_LIST, JONGSUNG_LIST,
)


# Build reverse maps
_BRAILLE_TO_CHO = {v: k for k, v in CHOSUNG_BRAILLE.items() if v}
_BRAILLE_TO_JUNG = {v: k for k, v in JUNGSUNG_BRAILLE.items() if v}
_BRAILLE_TO_JONG = {v: k for k, v in JONGSUNG_BRAILLE.items() if v}
_BRAILLE_TO_DIGIT = {v: k for k, v in KO_DIGIT_BRAILLE.items()}
_BRAILLE_TO_PUNCT = {v: k for k, v in KO_PUNCT_BRAILLE.items()}


def _compose_hangul(cho: str, jung: str, jong: str = '') -> str:
    """Compose Hangul syllable from jamo."""
    cho_idx = CHOSUNG_LIST.index(cho)
    jung_idx = JUNGSUNG_LIST.index(jung)
    jong_idx = JONGSUNG_LIST.index(jong) if jong else 0
    code = 0xAC00 + (cho_idx * 21 + jung_idx) * 28 + jong_idx
    return chr(code)


def decode_korean_braille(braille: str) -> str:
    """Decode Korean braille to Korean text."""
    result = []
    chars = list(braille)
    i = 0
    n = len(chars)
    in_number = False

    while i < n:
        ch = chars[i]

        # Space
        if ch == '\u2800':
            result.append(' ')
            in_number = False
            i += 1
            continue

        # Newline
        if ch == '\n':
            result.append('\n')
            in_number = False
            i += 1
            continue

        # Number indicator
        if ch == KO_NUMBER_INDICATOR:
            in_number = True
            i += 1
            continue

        # Digit
        if in_number and ch in _BRAILLE_TO_DIGIT:
            result.append(_BRAILLE_TO_DIGIT[ch])
            i += 1
            continue

        # Non-digit exits number mode
        if in_number:
            in_number = False

        # Try to read a Hangul syllable: 초성 + 중성 + (optional 종성)
        # Look for 초성
        if ch in _BRAILLE_TO_CHO:
            cho = _BRAILLE_TO_CHO[ch]
            i += 1

            # Look for 중성
            if i < n and chars[i] in _BRAILLE_TO_JUNG:
                jung = _BRAILLE_TO_JUNG[chars[i]]
                i += 1

                # Look for 종성 (greedy: try 2-char jong first, then 1-char)
                jong = ''
                if i + 1 < n:
                    two_char = chars[i] + chars[i + 1]
                    if two_char in _BRAILLE_TO_JONG:
                        jong = _BRAILLE_TO_JONG[two_char]
                        i += 2
                    elif chars[i] in _BRAILLE_TO_JONG and (i + 1 >= n or chars[i + 1] not in _BRAILLE_TO_JUNG):
                        # Only consume as jong if next char is NOT a vowel
                        # (otherwise it's the 초성 of the next syllable)
                        jong = _BRAILLE_TO_JONG[chars[i]]
                        i += 1
                elif i < n and chars[i] in _BRAILLE_TO_JONG:
                    if i + 1 >= n or chars[i + 1] not in _BRAILLE_TO_JUNG:
                        jong = _BRAILLE_TO_JONG[chars[i]]
                        i += 1

                result.append(_compose_hangul(cho, jung, jong))
                continue
            else:
                # 초성 without 중성 — just output the consonant character
                result.append(cho)
                continue

        # Try punctuation (multi-char first)
        matched_punct = False
        for plen in range(2, 0, -1):
            if i + plen <= n:
                seq = ''.join(chars[i:i + plen])
                if seq in _BRAILLE_TO_PUNCT:
                    result.append(_BRAILLE_TO_PUNCT[seq])
                    i += plen
                    matched_punct = True
                    break
        if matched_punct:
            continue

        # Unknown — pass through
        result.append(ch)
        i += 1

    return ''.join(result)

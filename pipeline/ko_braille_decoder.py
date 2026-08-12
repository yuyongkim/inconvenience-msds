"""
Korean Braille Decoder.

Reverse of ko_braille.py — converts Korean braille back to Korean text.
Used for round-trip validation (encode→decode should return original where the
mapping is not inherently ambiguous).
"""

from __future__ import annotations

from collections import defaultdict

from pipeline.brf_tables import BRAILLE_TO_ASCII
from pipeline.ko_braille import (
    CHOSUNG_BRAILLE,
    JUNGSUNG_BRAILLE,
    JONGSUNG_BRAILLE,
    KO_NUMBER_INDICATOR,
    KO_DIGIT_BRAILLE,
    KO_PUNCT_BRAILLE,
    CHOSUNG_LIST,
    JUNGSUNG_LIST,
    JONGSUNG_LIST
)


_BRAILLE_TO_CHO = {v: k for k, v in CHOSUNG_BRAILLE.items() if v}
_BRAILLE_TO_JUNG = {v: k for k, v in JUNGSUNG_BRAILLE.items() if v}
_BRAILLE_TO_JONG = {v: k for k, v in JONGSUNG_BRAILLE.items() if v}
_BRAILLE_TO_DIGIT = {v: k for k, v in KO_DIGIT_BRAILLE.items()}

_BRAILLE_TO_PUNCT_CANDIDATES: dict[str, list[str]] = defaultdict(list)
for punct, seq in KO_PUNCT_BRAILLE.items():
    _BRAILLE_TO_PUNCT_CANDIDATES[seq].append(punct)

_BRAILLE_TO_LATIN = {
    braille: ascii_ch
    for braille, ascii_ch in BRAILLE_TO_ASCII.items()
    if len(ascii_ch) == 1 and ascii_ch.isalpha() and ascii_ch.islower()
}

_ROMAN_INDICATOR = chr(0x2834)
_CAPITAL_INDICATOR = chr(0x2820)
_BRAILLE_SPACE = chr(0x2800)

_CHO_LENS = sorted({len(seq) for seq in _BRAILLE_TO_CHO}, reverse=True)
_JUNG_LENS = sorted({len(seq) for seq in _BRAILLE_TO_JUNG}, reverse=True)
_JONG_LENS = sorted({len(seq) for seq in _BRAILLE_TO_JONG}, reverse=True)
_PUNCT_LENS = sorted({len(seq) for seq in _BRAILLE_TO_PUNCT_CANDIDATES}, reverse=True)
_OPENING_BRACKETS = {seq for ch, seq in KO_PUNCT_BRAILLE.items() if ch in "([{"}
_CLOSING_BRACKETS = {seq for ch, seq in KO_PUNCT_BRAILLE.items() if ch in ")}]"}



def _compose_hangul(cho: str, jung: str, jong: str = "") -> str:
    """Compose Hangul syllable from jamo."""
    cho_idx = CHOSUNG_LIST.index(cho)
    jung_idx = JUNGSUNG_LIST.index(jung)
    jong_idx = JONGSUNG_LIST.index(jong) if jong else 0
    code = 0xAC00 + (cho_idx * 21 + jung_idx) * 28 + jong_idx
    return chr(code)


def _match(chars: list[str], start: int, mapping: dict[str, str], lengths: list[int]) -> tuple[str, int] | None:
    """Return the longest matching sequence/value pair from start."""
    for length in lengths:
        end = start + length
        if end > len(chars):
            continue
        seq = "".join(chars[start:end])
        value = mapping.get(seq)
        if value is not None:
            return value, length
    return None


def _punct_candidates(chars: list[str], start: int) -> list[tuple[str, int]]:
    matches: list[tuple[str, int]] = []
    for length in _PUNCT_LENS:
        end = start + length
        if end > len(chars):
            continue
        seq = "".join(chars[start:end])
        for punct in _BRAILLE_TO_PUNCT_CANDIDATES.get(seq, []):
            matches.append((punct, length))
    return matches


def _can_start_hangul(chars: list[str], start: int) -> bool:
    cho_match = _match(chars, start, _BRAILLE_TO_CHO, _CHO_LENS)
    if cho_match is None:
        return False
    _, cho_len = cho_match
    return _match(chars, start + cho_len, _BRAILLE_TO_JUNG, _JUNG_LENS) is not None


def _consume_hangul_syllable(chars: list[str], start: int) -> int | None:
    """Return consumed cell count for one clean Hangul syllable, else None."""
    cho_match = _match(chars, start, _BRAILLE_TO_CHO, _CHO_LENS)
    if cho_match is None:
        return None
    _, cho_len = cho_match
    jung_match = _match(chars, start + cho_len, _BRAILLE_TO_JUNG, _JUNG_LENS)
    if jung_match is None:
        return None
    _, jung_len = jung_match
    cursor = start + cho_len + jung_len

    punct_after = _prefer_punctuation(chars, cursor, allow_quote=False)
    strong_punct_after = punct_after is not None and punct_after[0] != "'"
    jong_match = _match(chars, cursor, _BRAILLE_TO_JONG, _JONG_LENS)
    if jong_match is not None and not strong_punct_after:
        _, jong_len = jong_match
        if _can_start_hangul(chars, cursor + jong_len) or not _can_start_hangul(chars, cursor):
            cursor += jong_len

    return cursor - start


def _should_break_latin_for_hangul(chars: list[str], start: int) -> bool:
    """Heuristic: stop a Latin span only when a clean Hangul run starts here."""
    consumed = _consume_hangul_syllable(chars, start)
    if consumed is None:
        return False
    cursor = start + consumed
    if cursor >= len(chars) or chars[cursor] in {_BRAILLE_SPACE, "\n", KO_NUMBER_INDICATOR, _ROMAN_INDICATOR}:
        return True
    if _consume_hangul_syllable(chars, cursor) is not None:
        return True
    punct = _prefer_punctuation(chars, cursor, allow_quote=False)
    return punct is not None


def _prefer_punctuation(
    chars: list[str],
    start: int,
    *,
    decoded_so_far: list[str] | None = None,
    paren_depth: int = 0,
    quote_open: bool = False,
    allow_quote: bool = True,
) -> tuple[str, int] | None:
    candidates = _punct_candidates(chars, start)
    if not candidates:
        return None

    prev_char = chars[start - 1] if start > 0 else None
    next_char = chars[start + 1] if start + 1 < len(chars) else None
    prev_decoded = decoded_so_far[-1] if decoded_so_far else ""
    prev_nonspace = next((ch for ch in reversed(decoded_so_far or []) if ch not in {" ", "\n"}), "")
    prev_token_chars: list[str] = []
    for ch in reversed(decoded_so_far or []):
        if ch in {" ", "\n"}:
            break
        if ch.isalnum():
            prev_token_chars.append(ch)
            continue
        break
    prev_token = "".join(reversed(prev_token_chars))
    punct_set = {punct for punct, _ in candidates}
    quote_open_context = prev_decoded in {"", " ", "\n", "(", "[", "{", "-", "—"}
    repeated_same_cell = (
        (start > 0 and chars[start - 1] == chars[start])
        or (start + 1 < len(chars) and chars[start + 1] == chars[start])
    )

    for punct, length in candidates:
        if length > 1:
            return punct, length

        if punct_set == {'"', '?'}:
            if not allow_quote:
                if next_char in {None, _BRAILLE_SPACE, "\n"}:
                    return "?", length
                continue
            if quote_open:
                if start + 1 < len(chars) and chars[start + 1] == chars[start]:
                    return "?", length
                if next_char in {None, _BRAILLE_SPACE, "\n"}:
                    return ('"', length) if prev_decoded in {".", "?", "!"} else ("?", length)
                if next_char and (
                    _can_start_hangul(chars, start + 1)
                    or next_char in {_ROMAN_INDICATOR, KO_NUMBER_INDICATOR}
                ):
                    return '"', length
            else:
                if quote_open_context and next_char and (
                    _can_start_hangul(chars, start + 1)
                    or next_char in {_ROMAN_INDICATOR, KO_NUMBER_INDICATOR}
                ):
                    return '"', length
            if next_char in {None, _BRAILLE_SPACE, "\n"}:
                return "?", length
            continue

        if punct == '"':
            if allow_quote and next_char and (
                _can_start_hangul(chars, start + 1)
                or next_char in {_ROMAN_INDICATOR, KO_NUMBER_INDICATOR}
            ):
                return punct, length
            continue

        if punct == '?':
            if start + length >= len(chars) or next_char in {_BRAILLE_SPACE, "\n", None}:
                return punct, length
            continue

        if punct in {".", "?", "!", ";", ":", '"', "'"}:
            if start + length >= len(chars) or next_char in {_BRAILLE_SPACE, "\n", None}:
                return punct, length

        if punct in {",", ".", "?", "!", ";", ":", '"', "'"}:
            if next_char and next_char not in _BRAILLE_TO_JUNG and not _can_start_hangul(chars, start):
                return punct, length

        # Brackets carry their own two-cell forms since the 2017 revision, so the
        # 3-6 cell is unambiguously 붙임표. The guesswork this used to need
        # (paren depth, neighbouring indicators) is gone with it.
        if punct == "-":
            return punct, length

    return None


def _decode_latin(chars: list[str], start: int, *, bracket_open: bool = False) -> tuple[str, int]:
    """Decode a roman-indicated Latin span."""
    i = start + 1
    result: list[str] = []
    capitalize_next = False

    while i < len(chars):
        ch = chars[i]
        if ch in {_BRAILLE_SPACE, "\n", KO_NUMBER_INDICATOR, _ROMAN_INDICATOR}:
            break
        # Two-cell brackets overlap the Latin alphabet: 여는 소괄호 (⠓⠄) reads as
        # "h'" and 닫는 소괄호 (⠠⠚) as a capital J. Hand them back to the caller —
        # a closing bracket only when one is actually open.
        pair = "".join(chars[i:i + 2])
        if pair in _OPENING_BRACKETS or (bracket_open and pair in _CLOSING_BRACKETS):
            break
        if ch == _CAPITAL_INDICATOR:
            capitalize_next = True
            i += 1
            continue
        letter = _BRAILLE_TO_LATIN.get(ch)
        if letter is None:
            break
        if _should_break_latin_for_hangul(chars, i):
            next_index = i + 1
            if next_index >= len(chars) or chars[next_index] in {
                _BRAILLE_SPACE,
                "\n",
                KO_NUMBER_INDICATOR,
                _ROMAN_INDICATOR,
            } or _should_break_latin_for_hangul(chars, next_index):
                result.append(letter.upper() if capitalize_next else letter)
                capitalize_next = False
                i += 1
                break
            break
        result.append(letter.upper() if capitalize_next else letter)
        capitalize_next = False
        i += 1

    if not result:
        return _ROMAN_INDICATOR, 1
    return "".join(result), i - start



def _decode_number(chars: list[str], start: int, *, paren_depth: int = 0) -> tuple[str, int]:
    """Decode a numeric span that starts with the Korean number indicator."""
    i = start + 1
    out: list[str] = []

    while i < len(chars):
        ch = chars[i]
        if out and _can_start_hangul(chars, i):
            break
        if ch in {_BRAILLE_SPACE, "\n", _ROMAN_INDICATOR}:
            break
        if ch == KO_NUMBER_INDICATOR:
            i += 1
            continue
        if ch in _BRAILLE_TO_DIGIT:
            out.append(_BRAILLE_TO_DIGIT[ch])
            i += 1
            continue

        punct_choice = _prefer_punctuation(chars, i, paren_depth=paren_depth)
        if punct_choice is not None:
            punct, punct_len = punct_choice
            if punct in {".", ",", "-", ":", ";", "/", "(", ")"}:
                if punct in {"(", ")"} and paren_depth == 0:
                    out.append("-")
                else:
                    out.append(punct)
                i += punct_len
                continue
        break

    return "".join(out), i - start


def decode_korean_braille(braille: str) -> str:
    """Decode Korean braille to Korean text."""
    result: list[str] = []
    chars = list(braille)
    i = 0
    n = len(chars)
    in_number = False
    paren_depth = 0
    quote_open = False

    while i < n:
        ch = chars[i]

        if ch == _BRAILLE_SPACE:
            result.append(" ")
            in_number = False
            i += 1
            continue

        if ch == "\n":
            result.append("\n")
            in_number = False
            i += 1
            continue

        if ch == KO_NUMBER_INDICATOR:
            decoded_number, consumed = _decode_number(chars, i, paren_depth=paren_depth)
            result.append(decoded_number)
            i += consumed
            continue

        if in_number:
            in_number = False

        if ch == _ROMAN_INDICATOR:
            latin, consumed = _decode_latin(chars, i, bracket_open=paren_depth > 0)
            result.append(latin)
            i += consumed
            continue

        punct_choice = _prefer_punctuation(
            chars,
            i,
            decoded_so_far=result,
            paren_depth=paren_depth,
            quote_open=quote_open,
        )

        cho_match = _match(chars, i, _BRAILLE_TO_CHO, _CHO_LENS)
        if cho_match is not None:
            cho, cho_len = cho_match
            jung_match = _match(chars, i + cho_len, _BRAILLE_TO_JUNG, _JUNG_LENS)
            if jung_match is not None:
                jung, jung_len = jung_match
                after_jung = i + cho_len + jung_len
                jong = ""
                jong_len = 0

                punct_after = _prefer_punctuation(
                    chars,
                    after_jung,
                    decoded_so_far=result,
                    paren_depth=paren_depth,
                    quote_open=quote_open,
                    allow_quote=quote_open,
                )
                jong_match = _match(chars, after_jung, _BRAILLE_TO_JONG, _JONG_LENS)
                strong_punct_after = punct_after is not None and punct_after[0] != "'"

                if jong_match is not None:
                    candidate_jong, candidate_len = jong_match
                    if not strong_punct_after and _can_start_hangul(chars, after_jung + candidate_len):
                        jong, jong_len = candidate_jong, candidate_len
                    elif not strong_punct_after and not _can_start_hangul(chars, after_jung):
                        jong, jong_len = candidate_jong, candidate_len
                elif not strong_punct_after and not _can_start_hangul(chars, after_jung):
                    jong_match = _match(chars, after_jung, _BRAILLE_TO_JONG, _JONG_LENS)
                    if jong_match is not None:
                        jong, jong_len = jong_match

                result.append(_compose_hangul(cho, jung, jong))
                i = after_jung + jong_len
                continue

            punct_choice = _prefer_punctuation(
                chars,
                i,
                decoded_so_far=result,
                paren_depth=paren_depth,
                quote_open=quote_open,
            )
            if punct_choice is not None:
                punct, punct_len = punct_choice
                result.append(punct)
                if punct == "(":
                    paren_depth += 1
                elif punct == ")" and paren_depth > 0:
                    paren_depth -= 1
                elif punct == '"':
                    quote_open = not quote_open
                i += punct_len
                continue

            result.append(cho)
            i += cho_len
            continue

        if punct_choice is not None:
            punct, punct_len = punct_choice
            result.append(punct)
            if punct == "(":
                paren_depth += 1
            elif punct == ")" and paren_depth > 0:
                paren_depth -= 1
            elif punct == '"':
                quote_open = not quote_open
            i += punct_len
            continue

        if ch == _CAPITAL_INDICATOR:
            result.append(ch)
            i += 1
            continue

        result.append(ch)
        i += 1

    return "".join(result)

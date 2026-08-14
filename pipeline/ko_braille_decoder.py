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
    NUMBER_CONNECTORS,
    CHOSUNG_BRAILLE,
    JUNGSUNG_BRAILLE,
    JONGSUNG_BRAILLE,
    KO_NUMBER_INDICATOR,
    KO_DIGIT_BRAILLE,
    KO_PUNCT_BRAILLE,
    CHOSUNG_LIST,
    JUNGSUNG_LIST,
    JONGSUNG_LIST,
    A_ABBREV,
    VOWEL_ABBREV,
    GEOT_ABBREV,
    TENSE_MARK,
    TENSE_BASE,
    WORD_ABBREV,
    JONG_PARTS,
    YEONG_CONSONANTS,
    LINK_MARK,
    AE_LINK_VOWELS,
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

# 약자·약어를 되읽기 위한 역표 (제12~18항)
_CELL_TO_A_ABBREV = {cell: cho for cho, cell in A_ABBREV.items()}
_CELL_TO_VOWEL_ABBREV = {cell: pair for pair, cell in VOWEL_ABBREV.items()}
_CELLS_TO_WORD = {cells: word for word, cells in WORD_ABBREV.items()}
_TENSE_OF = {base: tense for tense, base in TENSE_BASE.items()}
_JONG_JOIN = {parts: whole for whole, parts in JONG_PARTS.items()}

_ROMAN_INDICATOR = chr(0x2834)
_CAPITAL_INDICATOR = chr(0x2820)
_BRAILLE_SPACE = chr(0x2800)

_CHO_LENS = sorted({len(seq) for seq in _BRAILLE_TO_CHO}, reverse=True)
_JUNG_LENS = sorted({len(seq) for seq in _BRAILLE_TO_JUNG}, reverse=True)
_JONG_LENS = sorted({len(seq) for seq in _BRAILLE_TO_JONG}, reverse=True)
_PUNCT_LENS = sorted({len(seq) for seq in _BRAILLE_TO_PUNCT_CANDIDATES}, reverse=True)
_OPENING_BRACKETS = {seq for ch, seq in KO_PUNCT_BRAILLE.items() if ch in "([{"}
_CLOSING_BRACKETS = {seq for ch, seq in KO_PUNCT_BRAILLE.items() if ch in ")}]"}
_SPACE_AFTER_PUNCT = {".", "?", "!"}
_PERIOD_CELL = KO_PUNCT_BRAILLE["."]
_QUESTION_CELL = KO_PUNCT_BRAILLE["?"]
# 국어에 없는 첫소리+모음 짝. 쉼표(⠐)가 첫소리 ㄹ과 같은 칸이라 "눈,의류"가
# '릐'로 읽히던 자리를 막는다.
_IMPOSSIBLE_SYLLABLES = {("ㄹ", "ㅢ")}
# 로마자 구간 안의 부호. 같은 점형을 여럿이 나눠 쓸 때(⠦ = 물음표·큰따옴표)는
# 로마자 사이에 실제로 나오는 쪽을 고른다.
_ROMAN_PUNCT = {KO_PUNCT_BRAILLE[ch]: ch for ch in ("'", "?", ".", ",", ":", ";", "-")}
# 종성 ㅌ(⠦)은 물음표·큰따옴표와, 종성 ㅍ(⠲)과 겹받침 ㄿ(⠂⠲)의 끝 칸은 온점과
# 같은 칸이다. 국어에서 그 받침을 쓰는 음절은 아래가 사실상 전부다.
_JONG_P_SYLLABLES = frozenset("갚겊깊높늪덮릎섶숲앞엎옆잎짚") | {"읊"}
_JONG_T_SYLLABLES = frozenset("겉곁끝낱뭍밑밭볕뱉붙샅솥숱얕옅짙팥같맡흩")



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
    return _read_syllable(chars, start) is not None


def _is_braille(ch: str) -> bool:
    return "⠀" <= ch <= "⣿"


def _at_boundary(chars: list[str], index: int) -> bool:
    return index >= len(chars) or chars[index] in {_BRAILLE_SPACE, "\n"}


def _jong_candidates(chars: list[str], start: int) -> list[tuple[str, int]]:
    """종성으로 읽을 수 있는 후보를 긴 것부터 돌려준다."""
    out: list[tuple[str, int]] = []
    for length in _JONG_LENS:
        end = start + length
        if end > len(chars):
            continue
        value = _BRAILLE_TO_JONG.get("".join(chars[start:end]))
        if value is not None:
            out.append((value, length))
    return out


def _jong_spelling_exists(chars: list[str], start: int, syllable: str, jong_len: int) -> bool:
    """종성의 마지막 칸이 온점(⠲)과 겹칠 때, 그런 음절이 실제로 있는지.

    ⠲은 온점이면서 종성 ㅍ이고, 겹받침 ㄿ의 끝 칸이기도 하다. 두 읽기를 가르는
    규정상의 단서가 없으므로 국어에서 그 받침을 쓰는 음절인지로 가른다.
    """
    # 여는 괄호의 첫 칸(⠦)은 종성 ㅌ과 같다. "…을(를)"의 ⠦은 받침이 아니라 괄호의
    # 첫 칸이다 — 겹받침 후보가 그 칸을 물고 들어가는 것까지 막는다.
    for offset in (0, jong_len - 1):
        if "".join(chars[start + offset:start + offset + 2]) in _OPENING_BRACKETS:
            return False
    last = chars[start + jong_len - 1]
    if last == _QUESTION_CELL:
        return syllable in _JONG_T_SYLLABLES
    if last != _PERIOD_CELL:
        return True
    return syllable in _JONG_P_SYLLABLES


def _jong_reading_preferred(chars: list[str], start: int, punct: str, length: int) -> bool:
    """True when the cell cannot be the sentence mark it looks like.

    온점·물음표·느낌표 뒤에는 한 칸을 띄우므로, 그 칸 없이 한글이 곧바로 이어지면
    그 점형은 문장 부호가 아니라 종성이다 — 종성 ㅍ은 온점과, 종성 ㅌ은 물음표와
    같은 칸을 쓴다.
    """
    if punct not in _SPACE_AFTER_PUNCT:
        return False
    after = start + length
    if _at_boundary(chars, after):
        # 뒤가 비어 있으면 문장을 끝낸 부호로 읽는다. "앞 뒤"의 ⠲과 "…금지."의
        # ⠲은 여기서 갈리지 않지만, MSDS 문장은 압도적으로 부호 쪽이다.
        return False
    return _can_start_hangul(chars, after)


def _pick_jong(
    chars: list[str],
    start: int,
    cho: str,
    jung: str,
    punct_after: tuple[str, int] | None,
) -> tuple[str, int]:
    """Choose the 종성 reading at `start`, or ("", 0) when the cell is not one."""
    strong_punct = punct_after is not None and punct_after[0] != "'"
    for jong, jong_len in _jong_candidates(chars, start):
        syllable = _compose_hangul(cho, jung, jong)
        if not _jong_spelling_exists(chars, start, syllable, jong_len):
            continue
        if strong_punct and not _jong_reading_preferred(chars, start, *punct_after):
            continue
        if _can_start_hangul(chars, start + jong_len) or not _can_start_hangul(chars, start):
            return jong, jong_len
    return "", 0


def _read_syllable(chars: list[str], start: int) -> tuple[str, int] | None:
    """한 음절을 읽어 (글자, 소비한 칸 수)로 돌려준다.

    첫소리 ㅇ이 적히지 않고(제2항) 약자가 섞여 들어오므로(제12~17항), 칸을 앞에서
    부터 순서대로 벗겨 낸다: 된소리 표 → 첫소리 → 모음(또는 모음 약자) → 받침.
    """
    i = start
    if i >= len(chars):
        return None

    # 제12·15항 — '것'과 '껏'
    if "".join(chars[i:i + len(GEOT_ABBREV)]) == GEOT_ABBREV:
        return "것", len(GEOT_ABBREV)
    if chars[i] == TENSE_MARK and "".join(chars[i + 1:i + 1 + len(GEOT_ABBREV)]) == GEOT_ABBREV:
        return "껏", 1 + len(GEOT_ABBREV)

    # 제14항 — 된소리 표 + '가'·'사'의 약자
    tense = False
    if chars[i] == TENSE_MARK and i + 1 < len(chars) and chars[i + 1] in _CELL_TO_A_ABBREV:
        base = _CELL_TO_A_ABBREV[chars[i + 1]]
        if base in _TENSE_OF and CHOSUNG_BRAILLE.get(base, "") != chars[i + 1]:
            tense = True
            i += 1

    cho = "ㅇ"
    consumed_cho = 0
    a_abbrev_cho = None
    if chars[i] in _CELL_TO_A_ABBREV and _CELL_TO_A_ABBREV[chars[i]] in ("ㄱ", "ㅅ"):
        # '가'와 '사'는 첫소리 글자와 다른 제 점형을 쓴다
        a_abbrev_cho = _CELL_TO_A_ABBREV[chars[i]]
        consumed_cho = 1
    else:
        cho_match = _match(chars, i, _BRAILLE_TO_CHO, _CHO_LENS)
        # 제2항 — 첫소리 'ㅇ'은 적지 않으므로 그 점형은 '운'의 약자다
        if cho_match is not None and cho_match[0] != "ㅇ":
            cho, consumed_cho = cho_match

    cursor = i + consumed_cho
    if tense:
        base = a_abbrev_cho if a_abbrev_cho else cho
        if base not in _TENSE_OF:
            return None
        cho = _TENSE_OF[base]
        a_abbrev_cho = a_abbrev_cho and cho

    # 제15·16항 — 모음으로 시작하는 약자
    abbrev = _CELL_TO_VOWEL_ABBREV.get(chars[cursor]) if cursor < len(chars) else None
    if abbrev is not None and a_abbrev_cho is None:
        jung, jong = abbrev
        # 제16항 — 'ㅅ, ㅆ, ㅈ, ㅉ, ㅊ' 다음의 '영' 약자는 '성·썽·정·쩡·청'이다.
        if (jung, jong) == ("ㅕ", "ㅇ") and cho in YEONG_CONSONANTS:
            jung = "ㅓ"
        cursor += 1
        tail = _match(chars, cursor, _BRAILLE_TO_JONG, _JONG_LENS)
        if "".join(chars[cursor:cursor + 2]) in _OPENING_BRACKETS:
            tail = None      # 여는 괄호의 첫 칸(⠦)은 종성 ㅌ과 같다 — "…을(를)"
        if tail is not None and (jong, tail[0]) in _JONG_JOIN:
            jong = _JONG_JOIN[(jong, tail[0])]
            cursor += tail[1]
        return _compose_hangul(cho, jung, jong), cursor - start

    jung_match = None
    if a_abbrev_cho is None and cursor < len(chars):
        jung_match = _match(chars, cursor, _BRAILLE_TO_JUNG, _JUNG_LENS)
    if jung_match is None:
        # 제12·13·14항 — 'ㅏ'를 생략한 약자. 약자 점형일 때에만 그렇게 읽는다.
        if a_abbrev_cho is None:
            base = TENSE_BASE.get(cho, cho)
            if consumed_cho == 0 or base not in A_ABBREV:
                return None
            if "".join(chars[i:i + consumed_cho]) != (
                (TENSE_MARK if base != cho else "") + A_ABBREV[base]
            ):
                return None
        cho = a_abbrev_cho or cho
        jong, jong_len = _pick_jong(chars, cursor, cho, "ㅏ", _prefer_punctuation(chars, cursor, allow_quote=False))
        return _compose_hangul(cho, "ㅏ", jong), cursor + jong_len - start

    jung, jung_len = jung_match
    if (cho, jung) in _IMPOSSIBLE_SYLLABLES:
        return None
    cursor += jung_len
    punct_after = _prefer_punctuation(chars, cursor, allow_quote=False)
    jong, jong_len = _pick_jong(chars, cursor, cho, jung, punct_after)
    return _compose_hangul(cho, jung, jong), cursor + jong_len - start


def _link_mark_here(chars: list[str], index: int, decoded: list[str]) -> bool:
    """제10·11항의 붙임표 자리인지 — 앞은 받침 없는 모음, 뒤는 '예' 또는 '애'."""
    prev = next((ch for ch in reversed(decoded) if ch), "")
    if not prev or not ("가" <= prev <= "힣"):
        return False
    offset = ord(prev) - 0xAC00
    if offset % 28:
        return False
    nxt = _read_syllable(chars, index + 1)
    if nxt is None or not nxt[0]:
        return False
    code = ord(nxt[0]) - 0xAC00
    if code < 0 or (code // 588) != CHOSUNG_LIST.index("ㅇ"):
        return False
    jung = JUNGSUNG_LIST[(code % 588) // 28]
    if jung == "ㅖ":
        return True
    return jung == "ㅐ" and JUNGSUNG_LIST[(offset % 588) // 28] in AE_LINK_VOWELS


def _has_vowel_cell(chars: list[str], start: int, *, explicit_only: bool = False) -> bool:
    """모음 칸을 실제로 적은 음절인가 — 약자 한 칸만으로 된 음절과 가른다.

    약자 점형은 로마자·숫자와 겹치는 것이 많아, 한 칸짜리 약자만 늘어놓은 것은
    한글이라는 근거가 약하다.
    """
    if _read_syllable(chars, start) is None:
        return False
    i = start
    if chars[i] == TENSE_MARK and i + 1 < len(chars) and chars[i + 1] in _CELL_TO_A_ABBREV:
        i += 1
    cho_match = _match(chars, i, _BRAILLE_TO_CHO, _CHO_LENS)
    if cho_match is not None and cho_match[0] != "ㅇ":
        i += cho_match[1]
    elif chars[i] in _CELL_TO_A_ABBREV:
        i += 1
    if i >= len(chars):
        return False
    if chars[i] in _CELL_TO_VOWEL_ABBREV:
        return not explicit_only
    return _match(chars, i, _BRAILLE_TO_JUNG, _JUNG_LENS) is not None


def _word_abbrev_at(chars: list[str], start: int) -> tuple[str, int] | None:
    """제18항 — 약어."""
    word = _CELLS_TO_WORD.get("".join(chars[start:start + 2]))
    return (word, 2) if word else None


def _consume_hangul_syllable(chars: list[str], start: int) -> int | None:
    """Return consumed cell count for one clean Hangul syllable, else None."""
    read = _read_syllable(chars, start)
    return None if read is None else read[1]


def _should_break_latin_for_hangul(chars: list[str], start: int) -> bool:
    """Heuristic: stop a Latin span only when a clean Hangul run starts here.

    A Latin run carries no end marker, so the only place it can end without a
    space is where Hangul takes over — "Rat이". Requiring the Hangul reading to
    run all the way to the next boundary keeps Latin words whose cells happen to
    spell Hangul ("Magnesium" -> "Ma에머도" plus a leftover cell) intact.
    """
    if _consume_hangul_syllable(chars, start) is None:
        return False

    cursor = start
    while cursor < len(chars):
        if chars[cursor] in {_BRAILLE_SPACE, "\n", KO_NUMBER_INDICATOR, _ROMAN_INDICATOR}:
            return True
        consumed = _consume_hangul_syllable(chars, cursor)
        if consumed is None:
            return _prefer_punctuation(chars, cursor, allow_quote=False) is not None
        cursor += consumed
    return True


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
            # 닫는 괄호의 첫 칸은 한 칸짜리 부호와 겹친다 — 닫는 중괄호 ⠐⠚의 ⠐은
            # 쉼표다. 열린 괄호가 없는데 둘째 칸에서 한글이 시작되면 그 자리는
            # 괄호가 아니라 쉼표 뒤에 한글이 이어지는 자리다.
            if punct in ")}]" and any(other_len == 1 for _, other_len in candidates):
                # 닫는 중괄호 ⠐⠴은 쉼표 뒤에 로마자 표가 온 것과 점형이 같다.
                if paren_depth == 0 or _can_start_hangul(chars, start + 1):
                    continue
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
            if next_char and not _can_start_hangul(chars, start):
                return punct, length

        # Brackets carry their own two-cell forms since the 2017 revision, so the
        # 3-6 cell is unambiguously 붙임표. The guesswork this used to need
        # (paren depth, neighbouring indicators) is gone with it.
        if punct == "-":
            return punct, length

    return None


def _hangul_tail_to_boundary(
    chars: list[str], start: int, *, least: int = 1, raw_ends: bool = True
) -> bool:
    return _hangul_tail_count(chars, start, raw_ends=raw_ends) >= least


def _hangul_tail_count(
    chars: list[str], start: int, *, raw_ends: bool = True, strict_end: bool = False
) -> int:
    """여기서부터 어절 끝까지 이어지는 한글 음절 수. 한글이 아니면 0.

    약자 한 칸짜리 음절은 로마자·숫자와 겹치는 점형이라 세지 않는다(구간 중간에
    끼는 것은 그대로 지나간다). 문장 부호로 끝나는 짧은 run은 그 뒤가 비었을
    때에만 인정한다 — "nema.go.kr"의 마침표가 한글 구간으로 읽히지 않도록.
    """
    cursor = start
    seen = 0
    while cursor < len(chars):
        ch = chars[cursor]
        if ch in {_BRAILLE_SPACE, "\n"}:
            # 다음 어절도 한글이면 이어서 센다.
            if seen and seen < 3 and _can_start_hangul(chars, cursor + 1):
                cursor += 1
                continue
            return seen
        if not _is_braille(ch):
            # 점형이 없는 글자(빗금 등). 종료표를 가리는 자리에서는 어절 끝으로
            # 보지 않는다 — "nih.gov/cgi"가 통째로 한글로 읽히던 자리.
            return seen if raw_ends else 0
        consumed = _consume_hangul_syllable(chars, cursor)
        if consumed is not None:
            if _has_vowel_cell(chars, cursor):
                seen += 1
            cursor += consumed
            continue
        if not seen:
            return 0
        if seen >= 3 and not strict_end:
            return seen
        punct = _prefer_punctuation(chars, cursor, allow_quote=False)
        if punct is None or not _at_boundary(chars, cursor + punct[1]):
            return 0
        return seen
    return seen


def _latin_reaches_boundary(chars: list[str], start: int) -> bool:
    """여기서부터 어절 끝까지 로마자로 읽히는가.

    첫소리 ㅇ을 적지 않으면서(제2항) 모음 한 칸이 곧 한 음절이 되어, 로마자 구간
    안이 한글로도 읽히는 자리가 늘었다. 종료표가 없는 구간은 제33~35항이 정한
    자리에서만 끝나므로, 로마자로 계속 읽히는 동안에는 넘기지 않는다.
    """
    i = start
    while i < len(chars):
        ch = chars[i]
        if ch in {"\n", KO_NUMBER_INDICATOR, _ROMAN_INDICATOR}:
            return True
        pair = "".join(chars[i:i + 2])
        if pair in _OPENING_BRACKETS or pair in _CLOSING_BRACKETS:
            return True
        if not _is_braille(ch):
            # 점형이 없는 글자(빗금·세로줄)에서 구간이 끝난다 — "Daphnia magna|"
            return True
        if ch in _BRAILLE_TO_LATIN or ch in {_CAPITAL_INDICATOR, _BRAILLE_SPACE}:
            i += 1
            continue
        punct = _roman_punct_at(chars, i)
        if punct is None:
            return False
        i += punct[1]
    return True


def _latin_continues(chars: list[str], start: int) -> int:
    """로마자로 계속 읽히면 남은 글자 수, 아니면 0.

    로마자 뒤의 마침표는 종료표와 같은 칸이다(제30항). 이 수를 한글로 읽었을 때의
    음절 수와 견줘서 어느 쪽이 더 그럴듯한지 고른다 — "U.S. National"의 마침표는
    구간 안이고, "ppmV.에서"의 ⠲은 종료표다.
    """
    if not _latin_reaches_boundary(chars, start):
        return 0
    letters = 0
    for i in range(start, len(chars)):
        ch = chars[i]
        if ch in {"\n", KO_NUMBER_INDICATOR, _ROMAN_INDICATOR}:
            break
        pair = "".join(chars[i:i + 2])
        if pair in _OPENING_BRACKETS or pair in _CLOSING_BRACKETS:
            break
        if ch in _BRAILLE_TO_LATIN:
            letters += 1
    return letters


def _terminator_ahead(chars: list[str], start: int) -> bool:
    """앞쪽에 로마자 종료표가 있는가.

    여기서부터 로마자로 읽히는 동안 ⠲을 만나면 그것이 구간을 닫는 종료표다
    (제30항). 그러면 중간의 빈칸에서 구간을 끊으면 안 된다 — "Magnesium
    permanganate를"의 빈칸.
    """
    i = start
    while i < len(chars):
        ch = chars[i]
        if ch == _PERIOD_CELL:
            return True
        if ch == chr(10) or ch in {KO_NUMBER_INDICATOR, _ROMAN_INDICATOR}:
            return False
        pair = "".join(chars[i:i + 2])
        if pair in _OPENING_BRACKETS or pair in _CLOSING_BRACKETS:
            return False
        if ch in _BRAILLE_TO_LATIN or ch in {_CAPITAL_INDICATOR, _BRAILLE_SPACE} or not _is_braille(ch):
            i += 1
            continue
        punct = _roman_punct_at(chars, i)
        if punct is None:
            return False
        i += punct[1]
    return False


def _unterminated_roman_end(chars: list[str], start: int, bracket_open: bool) -> int:
    """구간 끝(제33~35항으로 종료표를 적지 않은 경우) 다음 자리를 찾는다.

    마지막 로마자까지가 구간이다. 그 사이의 빈칸·문장 부호는 제32항에 따라 구간
    안에 있는 것으로 보고, 한글이 어절 끝까지 이어지는 자리에서만 넘긴다.
    """
    i = start + 1
    last_letter = start
    while i < len(chars):
        ch = chars[i]
        if ch in {"\n", KO_NUMBER_INDICATOR, _ROMAN_INDICATOR}:
            break
        pair = "".join(chars[i:i + 2])
        all_latin = len(pair) == 2 and all(cell in _BRAILLE_TO_LATIN for cell in pair)
        if not all_latin and (pair in _OPENING_BRACKETS or (bracket_open and pair in _CLOSING_BRACKETS)):
            break
        if ch in _BRAILLE_TO_LATIN:
            last_letter = i
        elif ch == _CAPITAL_INDICATOR:
            pass
        elif ch == _BRAILLE_SPACE:
            # 종료표가 없는 구간은 제33~35항이 정한 자리, 곧 숫자나 문장 부호
            # 앞에서만 끝난다. 한글이 곧바로 이어지는 구간이라면 종료표가 있었을
            # 것이므로 여기서 한글을 찾아 끊지 않는다. 다만 표기가 규정을 따르지
            # 않는 입력도 있어, 빈칸 뒤가 한 어절 내내 한글이면 넘긴다.
            if (
                _hangul_tail_to_boundary(chars, i + 1, least=2)
                and not _latin_reaches_boundary(chars, i + 1)
                and not _terminator_ahead(chars, i + 1)
            ):
                break
        elif _is_braille(ch):
            # 구간 안의 부호는 로마자 사이에 나오는 쪽으로 읽는다 — 종료표로
            # 읽히지 않은 ⠲은 마침표("index.jsp"), ⠦은 물음표("htmlgen?")다.
            punct = _roman_punct_at(chars, i) or _prefer_punctuation(chars, i, allow_quote=False)
            if punct is None:
                break
            # 제33항 — 로마자와 한글 사이에 문장 부호가 오면 거기서 구간이 끝난다.
            # 그 부호가 ⠲이면 종료표일 수 있으므로 한 음절만 이어져도 넘긴다.
            least = 1 if ch == _PERIOD_CELL else 2
            tail = _hangul_tail_count(
                chars,
                i + punct[1],
                raw_ends=ch != _PERIOD_CELL,
                strict_end=ch == _PERIOD_CELL,
            )
            # 한 음절뿐인 한글 꼬리는 약한 근거다. 그 자리에서 로마자가 세 글자
            # 넘게 이어지면 구간 안의 마침표로 본다 — "U.S. National".
            if tail >= least and not (
                ch == _PERIOD_CELL and tail == 1 and _latin_continues(chars, i + 1) >= 3
            ) and (
                ch == _PERIOD_CELL or not _latin_reaches_boundary(chars, i + punct[1])
            ):
                break
            i += punct[1]      # 두 칸짜리 부호(쌍점 등)는 두 칸을 건너뛴다
            continue
        elif _hangul_tail_to_boundary(chars, i + 1, least=2) and not _latin_reaches_boundary(chars, i + 1):
            # 점형이 없는 글자(빗금 등)도 제33항의 그 문장 부호 자리다 — "MSDS/라벨".
            break
        i += 1
    return last_letter + 1


def _roman_punct_at(chars: list[str], index: int) -> tuple[str, int] | None:
    """로마자 구간 안에서 이 자리의 부호를 읽는다."""
    pair = "".join(chars[index:index + 2])
    if pair in _ROMAN_PUNCT:
        return _ROMAN_PUNCT[pair], 2
    if chars[index] in _ROMAN_PUNCT:
        return _ROMAN_PUNCT[chars[index]], 1
    return None


def _decode_roman(chars: list[str], start: int, end: int) -> str:
    """Read cells [start, end) as roman text."""
    out: list[str] = []
    capitalize_next = False
    i = start
    while i < end:
        ch = chars[i]
        if ch == _CAPITAL_INDICATOR:
            capitalize_next = True
            i += 1
            continue
        letter = _BRAILLE_TO_LATIN.get(ch)
        if letter is not None:
            out.append(letter.upper() if capitalize_next else letter)
            capitalize_next = False
            i += 1
            continue
        capitalize_next = False
        if ch == _BRAILLE_SPACE:
            out.append(" ")
            i += 1
            continue
        punct = _roman_punct_at(chars, i)
        if punct is not None:
            out.append(punct[0])
            i += punct[1]
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _decode_latin(chars: list[str], start: int, *, bracket_open: bool = False) -> tuple[str, int]:
    """Decode a roman span, with or without the 종료표 that should close it.

    제30항의 종료표는 구간의 마지막 로마자 바로 뒤에 온다. 그러니 구간의 끝을
    먼저 찾고, 그 자리에 ⠲이 있으면 그것이 종료표다. 제33~35항이 종료표를 적지
    않게 한 자리에는 그 칸이 없다.
    """
    end = _unterminated_roman_end(chars, start, bracket_open)
    if end <= start + 1:
        return _ROMAN_INDICATOR, 1
    text = _decode_roman(chars, start + 1, end)
    if end < len(chars) and chars[end] == _PERIOD_CELL and _reads_as_terminator(chars, end):
        return text, end + 1 - start
    return text, end - start


def _reads_as_terminator(chars: list[str], index: int) -> bool:
    """이 ⠲을 종료표로 읽을 자리인지.

    종료표는 뒤가 비었거나 한글이 이어질 때에만 적힌다(제30항, 제33~35항).
    괄호나 쌍점이 이어지는 자리의 ⠲은 종료표가 아니라 마침표다 — "UN No.)".
    """
    after = index + 1
    return _at_boundary(chars, after) or _can_start_hangul(chars, after)


def _decode_number(chars: list[str], start: int, *, paren_depth: int = 0) -> tuple[str, int]:
    """Decode a numeric span that starts with the Korean number indicator."""
    i = start + 1
    out: list[str] = []

    while i < len(chars):
        ch = chars[i]
        if out and _can_start_hangul(chars, i) and (
            chars[i] not in _BRAILLE_TO_DIGIT
            or (out[-1] in NUMBER_CONNECTORS and _has_vowel_cell(chars, i, explicit_only=True))
        ):
            # 제38항 [다만] — 숫자와 같은 칸으로 시작하는 한글 앞에는 빈칸이 있다.
            # 붙임표 따위로 이어진 자리(제39·49항)에서는 그 빈칸이 없으므로, 모음
            # 칸까지 갖춘 음절이면 거기서 수가 끝난 것으로 본다 — "3-메틸".
            break
        if ch in {_BRAILLE_SPACE, "\n", _ROMAN_INDICATOR}:
            break
        if ch == KO_NUMBER_INDICATOR:
            i += 1
            continue
        # 여는 소괄호 (⠓⠄) starts on the same cell as the digit 8, so a bracket
        # right after a number would be eaten as "8'". Hand brackets back to the
        # caller, which is the one place that tracks how deep we are — but only
        # when the pair cannot be digits: 여는 중괄호 ⠓⠁ and 대괄호 ⠓⠃ are the
        # cells for "81" and "82", and inside a number that is what they are.
        pair = "".join(chars[i:i + 2])
        all_digits = len(pair) == 2 and all(cell in _BRAILLE_TO_DIGIT for cell in pair)
        if not all_digits and (pair in _OPENING_BRACKETS or pair in _CLOSING_BRACKETS):
            break
        if ch in _BRAILLE_TO_DIGIT:
            out.append(_BRAILLE_TO_DIGIT[ch])
            i += 1
            continue

        punct_choice = _prefer_punctuation(chars, i, paren_depth=paren_depth)
        if punct_choice is not None:
            punct, punct_len = punct_choice
            if punct in {".", ",", "-", ":", ";", "/"}:
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

        # 제18항 — 약어
        abbrev_word = _word_abbrev_at(chars, i)
        if abbrev_word is not None and (not result or result[-1] in {" ", "\n", ""}):
            result.append(abbrev_word[0])
            i += abbrev_word[1]
            continue

        # 제10·11항 — 앞 음절과 '예'·'애' 사이의 붙임표는 글자가 아니다.
        if chars[i] == LINK_MARK and _link_mark_here(chars, i, result):
            i += 1
            continue

        syllable = _read_syllable(chars, i)
        if syllable is not None:
            result.append(syllable[0])
            i += syllable[1]
            continue

        if punct_choice is not None:
            punct, punct_len = punct_choice
            result.append(punct)
            if punct in "([{":
                paren_depth += 1
            elif punct in ")}]" and paren_depth > 0:
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

"""
Korean Braille Encoder.

Converts Korean text (한글) to Korean braille (점자) following
the Korean Braille Rules (한국 점자 규정).

Dot patterns validated against liblouis ko-g1 tables.

Reference: 한국점자규정 (문화체육관광부 고시)
"""

from __future__ import annotations


# ============================================================
# Hangul decomposition
# ============================================================

CHOSUNG_LIST = list('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')
JUNGSUNG_LIST = list('ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ')
JONGSUNG_LIST = [
    '', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ',
    'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ',
    'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ',
]


def decompose_hangul(ch: str) -> tuple[str, str, str] | None:
    code = ord(ch)
    if 0xAC00 <= code <= 0xD7A3:
        offset = code - 0xAC00
        jong = offset % 28
        jung = (offset // 28) % 21
        cho = offset // (28 * 21)
        return CHOSUNG_LIST[cho], JUNGSUNG_LIST[jung], JONGSUNG_LIST[jong]
    return None


# ============================================================
# Dot pattern to Unicode braille conversion
# ============================================================

def dots_to_braille(dot_string: str) -> str:
    """Convert dot number string like '1-2-4' or '135' to Unicode braille."""
    if not dot_string or dot_string == '0':
        return ''
    # Parse dots
    if '-' in dot_string:
        dots = [int(d) for d in dot_string.split('-') if d.isdigit()]
    else:
        dots = [int(d) for d in dot_string if d.isdigit()]
    # Build braille cell: dot N maps to bit (N-1)
    value = 0
    for d in dots:
        if 1 <= d <= 8:
            value |= (1 << (d - 1))
    return chr(0x2800 + value)


# ============================================================
# Korean braille dot patterns (from liblouis ko.cti / ko-g1-rules.cti)
# Using dot numbers: 1=top-left, 2=mid-left, 3=bot-left,
#                     4=top-right, 5=mid-right, 6=bot-right
# ============================================================

# 초성 (Initial consonants) — from liblouis
_CHO_DOTS = {
    'ㄱ': '4',        # dot 4
    'ㄲ': '6|4',      # ssang: dot6 (separate cell) + base
    'ㄴ': '1-4',      # dots 1,4
    'ㄷ': '2-4',      # dots 2,4
    'ㄸ': '6|2-4',    # ssang
    'ㄹ': '5',        # dot 5
    'ㅁ': '1-5',      # dots 1,5
    'ㅂ': '4-5',      # dots 4,5
    'ㅃ': '6|4-5',    # ssang
    'ㅅ': '6',        # dot 6 (confirmed by ref h2b.py)
    'ㅆ': '6|6',      # ssang: dot6 (cell1) + dot6 (cell2)
    'ㅇ': '1-2-4-5',  # dots 1,2,4,5
    'ㅈ': '4-6',      # dots 4,6 (confirmed by ref h2b.py)
    'ㅉ': '6|4-6',    # ssang
    'ㅊ': '5-6',      # dots 5,6
    'ㅋ': '1-2-4',    # dots 1,2,4
    'ㅌ': '1-2-5',    # dots 1,2,5
    'ㅍ': '1-4-5',    # dots 1,4,5
    'ㅎ': '2-4-5',    # dots 2,4,5
}

# 중성 (Vowels)
_JUNG_DOTS = {
    'ㅏ': '1-2-6',    # a
    'ㅐ': '1-2-3-5',  # ae
    'ㅑ': '3-4-5',    # ya
    'ㅒ': '3-4-5|1-2-3-5',  # yae = ㅑ + ㅐ (2 cells)
    'ㅓ': '2-3-4',    # eo
    'ㅔ': '1-3-4-5',  # e
    'ㅕ': '1-5-6',    # yeo
    'ㅖ': '3-4',      # ye
    'ㅗ': '1-3-6',    # o
    'ㅘ': '1-2-3-6',  # wa (o + a)
    'ㅙ': '1-2-3-6|1-2-3-5',  # wae = ㅘ + ㅐ (2 cells)
    'ㅚ': '1-3-4-5-6',  # oe (single cell)
    'ㅛ': '3-4-6',    # yo
    'ㅜ': '1-3-4',    # u
    'ㅝ': '1-2-3-4',  # wo (u + eo)
    'ㅞ': '1-2-3-4|1-2-3-5',  # we = ㅝ + ㅐ (2 cells)
    'ㅟ': '1-3-4|1-2-3-5',    # wi = ㅜ + ㅐ (2 cells)
    'ㅠ': '1-4-6',    # yu
    'ㅡ': '2-4-6',    # eu
    'ㅢ': '2-4-5-6',  # ui
    'ㅣ': '1-3-5',    # i
}

# 종성 (Final consonants)
# 종성: 겹받침은 두 셀로 분리 (각 자음의 종성 패턴을 순서대로)
_JONG_DOTS = {
    '': '',
    'ㄱ': '1',
    'ㄲ': '1|1',       # ㄱ+ㄱ
    'ㄳ': '1|3',       # ㄱ+ㅅ
    'ㄴ': '2-5',
    'ㄵ': '2-5|1-3',   # ㄴ+ㅈ
    'ㄶ': '2-5|3-5-6', # ㄴ+ㅎ
    'ㄷ': '3-5',
    'ㄹ': '2',
    'ㄺ': '2|1',       # ㄹ+ㄱ
    'ㄻ': '2|2-6',     # ㄹ+ㅁ
    'ㄼ': '2|1-2',     # ㄹ+ㅂ
    'ㄽ': '2|3',       # ㄹ+ㅅ
    'ㄾ': '2|2-3-6',   # ㄹ+ㅌ
    'ㄿ': '2|2-5-6',   # ㄹ+ㅍ
    'ㅀ': '2|3-5-6',   # ㄹ+ㅎ
    'ㅁ': '2-6',
    'ㅂ': '1-2',
    'ㅄ': '1-2|3',     # ㅂ+ㅅ
    'ㅅ': '3',
    'ㅆ': '3-4',       # dots 3,4 (single cell, per ref h2b.py)
    'ㅇ': '2-3-5-6',
    'ㅈ': '1-3',
    'ㅊ': '2-3',
    'ㅋ': '2-3-5',
    'ㅌ': '2-3-6',
    'ㅍ': '2-5-6',
    'ㅎ': '3-5-6',
}

# Pre-compute braille strings
CHOSUNG_BRAILLE = {}
for k, v in _CHO_DOTS.items():
    if '|' in v:
        CHOSUNG_BRAILLE[k] = ''.join(dots_to_braille(part) for part in v.split('|'))
    else:
        CHOSUNG_BRAILLE[k] = dots_to_braille(v)
JUNGSUNG_BRAILLE = {}
for k, v in _JUNG_DOTS.items():
    if '|' in v:
        JUNGSUNG_BRAILLE[k] = ''.join(dots_to_braille(part) for part in v.split('|'))
    else:
        JUNGSUNG_BRAILLE[k] = dots_to_braille(v)
JONGSUNG_BRAILLE = {}
for k, v in _JONG_DOTS.items():
    if not v:
        JONGSUNG_BRAILLE[k] = ''
    elif '|' in v:
        # Multi-cell (겹받침): each part is a separate cell
        JONGSUNG_BRAILLE[k] = ''.join(dots_to_braille(part) for part in v.split('|'))
    else:
        JONGSUNG_BRAILLE[k] = dots_to_braille(v)

# Number patterns (same as international braille)
KO_NUMBER_INDICATOR = dots_to_braille('3-4-5-6')  # ⠼
KO_DIGIT_BRAILLE = {
    '1': dots_to_braille('1'),
    '2': dots_to_braille('1-2'),
    '3': dots_to_braille('1-4'),
    '4': dots_to_braille('1-4-5'),
    '5': dots_to_braille('1-5'),
    '6': dots_to_braille('1-2-4'),
    '7': dots_to_braille('1-2-4-5'),
    '8': dots_to_braille('1-2-5'),
    '9': dots_to_braille('2-4'),
    '0': dots_to_braille('2-4-5'),
}

# Punctuation
KO_PUNCT_BRAILLE = {
    '.': dots_to_braille('2-5-6'),
    ',': dots_to_braille('5'),
    '?': dots_to_braille('2-3-6'),
    '!': dots_to_braille('4-5-6'),
    ':': dots_to_braille('5') + dots_to_braille('2'),
    ';': dots_to_braille('5-6'),
    '-': dots_to_braille('3-6'),
    '(': dots_to_braille('3-6'),
    ')': dots_to_braille('3-6'),
    '"': dots_to_braille('2-3-6'),
    "'": dots_to_braille('3'),
}


# ============================================================
# Main encoder
# ============================================================

def encode_korean_braille(text: str) -> str:
    """Encode Korean text to Korean braille (Unicode)."""
    result = []
    in_number = False
    in_latin = False

    for ch in text:
        if ch == ' ':
            result.append('\u2800')
            in_number = False
            in_latin = False
            continue

        if ch == '\n':
            result.append('\n')
            in_number = False
            in_latin = False
            continue

        # Hangul syllable
        decomposed = decompose_hangul(ch)
        if decomposed:
            in_number = False
            in_latin = False
            cho, jung, jong = decomposed

            # 초성
            if cho in CHOSUNG_BRAILLE:
                result.append(CHOSUNG_BRAILLE[cho])

            # 중성
            if jung in JUNGSUNG_BRAILLE:
                result.append(JUNGSUNG_BRAILLE[jung])

            # 종성
            if jong and jong in JONGSUNG_BRAILLE:
                result.append(JONGSUNG_BRAILLE[jong])

            continue

        # Digit
        if ch.isdigit():
            if not in_number:
                # Number indicator — cancels latin mode
                result.append(KO_NUMBER_INDICATOR)  # ⠼
                in_number = True
                in_latin = False
            result.append(KO_DIGIT_BRAILLE.get(ch, '\u2800'))
            continue

        # Latin letter
        if ch.isalpha() and ch.isascii():
            in_number = False
            if not in_latin:
                # Roman indicator ⠴ (dots 3-5-6)
                result.append('\u2834')
                in_latin = True
            # Capital letter
            if ch.isupper():
                result.append('\u2820')  # ⠠ capital indicator
                lower_ch = ch.lower()
            else:
                lower_ch = ch
            # Letter pattern (same as English braille letters)
            letter_patterns = {
                'a': '\u2801', 'b': '\u2803', 'c': '\u2809', 'd': '\u2819',
                'e': '\u2811', 'f': '\u280B', 'g': '\u281B', 'h': '\u2813',
                'i': '\u280A', 'j': '\u281A', 'k': '\u2805', 'l': '\u2807',
                'm': '\u280D', 'n': '\u281D', 'o': '\u2815', 'p': '\u280F',
                'q': '\u281F', 'r': '\u2817', 's': '\u280E', 't': '\u281E',
                'u': '\u2825', 'v': '\u2827', 'w': '\u283A', 'x': '\u282D',
                'y': '\u283D', 'z': '\u2835',
            }
            result.append(letter_patterns.get(lower_ch, '\u2800'))
            continue

        # Punctuation
        in_number = False
        in_latin = False
        if ch in KO_PUNCT_BRAILLE:
            result.append(KO_PUNCT_BRAILLE[ch])
            continue

        # Other — pass through
        result.append(ch)

    return ''.join(result)

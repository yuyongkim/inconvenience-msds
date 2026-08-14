"""
Korean Braille Encoder.

Converts Korean text (한글) to Korean braille (점자) following
the Korean Braille Rules (한국 점자 규정).

Dot patterns validated against liblouis ko-g1 tables.

Reference: 한국점자규정 (문화체육관광부 고시)
"""

from __future__ import annotations

import string


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
    '?': dots_to_braille('2-3-6'),          # 제45항
    '!': dots_to_braille('2-3-5'),          # 제46항
    ':': dots_to_braille('5') + dots_to_braille('2'),        # 제49항
    ';': dots_to_braille('5-6') + dots_to_braille('2-3'),    # 제50항
    '-': dots_to_braille('3-6'),            # 제59항
    # Brackets are two cells under the 2017 revision (제54-56항). The revision
    # moved them off the single 3-6 cell precisely because that cell was shared
    # with 붙임표 and 줄표; see data/standards/README.md for the source pages.
    '(': dots_to_braille('2-3-6') + dots_to_braille('3'),
    ')': dots_to_braille('6') + dots_to_braille('3-5-6'),
    '{': dots_to_braille('2-3-6') + dots_to_braille('2'),
    '}': dots_to_braille('5') + dots_to_braille('3-5-6'),
    '[': dots_to_braille('2-3-6') + dots_to_braille('2-3'),
    ']': dots_to_braille('5-6') + dots_to_braille('3-5-6'),
    # 제52·53항의 따옴표는 아직 넣지 않았다. 닫는 큰따옴표(⠴)가 로마자 표·종성
    # ㅎ과 같은 칸이라, 여닫이를 나누려면 그 셋을 함께 가릴 방법이 필요하다.
    '"': dots_to_braille('2-3-6'),
    "'": dots_to_braille('3'),          # 제69항 아포스트로피
}


# 제10항 — '예'의 점형(⠌)은 쌍시옷 받침과 같다. 앞 음절이 모음으로 끝나면 그
# 자리가 받침으로 읽히므로 사이에 붙임표를 적는다.
# 제11항 — 'ㅑ, ㅘ, ㅜ, ㅝ' 뒤의 '애'도 같은 이유로 붙임표를 적는다.
LINK_MARK = dots_to_braille('3-6')
AE_LINK_VOWELS = frozenset(('ㅑ', 'ㅘ', 'ㅜ', 'ㅝ'))


def _needs_link_mark(prev: tuple[str, str, str] | None, cur: tuple[str, str, str]) -> bool:
    if prev is None or prev[2]:
        return False
    cho, jung, _ = cur
    if cho != 'ㅇ':
        return False
    if jung == 'ㅖ':
        return True
    return jung == 'ㅐ' and prev[1] in AE_LINK_VOWELS


# 제38항 [다만] — 숫자와 혼동되는 'ㄴ, ㄷ, ㅁ, ㅋ, ㅌ, ㅍ, ㅎ'의 첫소리 글자와
# '운'의 약자가 숫자 다음에 이어 나올 때에는 띄어 쓴다. 모두 숫자와 같은 칸이다.
DIGIT_LOOKALIKE_CELLS = frozenset(
    CHOSUNG_BRAILLE[c] for c in 'ㄴㄷㅁㅋㅌㅍㅎ'
) | {dots_to_braille('1-2-4-5')}

# 제39·49항 — 붙임표나 쌍점으로 이어진 숫자에는 수표를 다시 적지 않는다. 소수점과
# 자릿점 쉼표도 같다(영어 점자 규정, 제47항 [다만]).
NUMBER_CONNECTORS = frozenset('-:.,')

# 로마자 표(제30항). 종료표는 마침표와 같은 칸이며, 로마자 뒤에 마침표가 올
# 때에는 두 번 적지 않고 한 번만 적는다.
KO_ROMAN_INDICATOR = dots_to_braille('3-5-6')      # ⠴
KO_ROMAN_TERMINATOR = dots_to_braille('2-5-6')     # ⠲

# 로마자 사이에 끼어도 구간을 끊지 않는 부호. 제32항이 "로마자가 둘 이상 연이어
# 나올 때에는 로마자 표는 첫 로마자 앞에만" 적게 하므로, 이들 뒤에 다시 로마자가
# 나오면 같은 구간이다. 괄호·따옴표는 제34항이 따로 다룬다.
_ROMAN_CONNECTORS = frozenset(' ' + ''.join(
    ch for ch in string.punctuation if ch not in '()[]{}"'
))


def _roman_span_end(text: str, start: int) -> int:
    """Index just past the roman span beginning at `start` (제30·32항)."""
    i = start
    last_letter = start
    while i < len(text):
        ch = text[i]
        if ch.isascii() and ch.isalpha():
            last_letter = i
        elif ch not in _ROMAN_CONNECTORS:
            break
        i += 1
    return last_letter + 1


def _roman_terminator_needed(text: str, end: int) -> bool:
    """제30항의 종료표를 적는 자리인지. 제33·34·35항이 적지 않는 자리를 정한다."""
    if end >= len(text):
        return True
    nxt = text[end]
    if nxt.isdigit():
        return False                      # \uc81c35\ud56d \u2014 \ub85c\ub9c8\uc790\uc640 \uc22b\uc790\uac00 \uc774\uc5b4 \ub098\uc62c \ub54c
    if nxt in ' \n' or decompose_hangul(nxt):
        return True
    return False                          # \uc81c33\u00b734\ud56d \u2014 \ubb38\uc7a5 \ubd80\ud638\uac00 \uc774\uc5b4 \ub098\uc62c \ub54c



# ============================================================
# 약자·약어 (제12~18항)
# ============================================================

# 제12항 — 'ㅏ'가 붙은 음절의 약자. '가'와 '사'는 별도의 점형을 쓰고, 나머지는
# 'ㅏ'를 생략하고 첫소리 글자만 적는다. '라'와 '차'는 약자가 없다.
A_ABBREV = {
    'ㄱ': dots_to_braille('1-2-4-6'),   # 가
    'ㅅ': dots_to_braille('1-2-3'),     # 사
    'ㄴ': CHOSUNG_BRAILLE['ㄴ'],
    'ㄷ': CHOSUNG_BRAILLE['ㄷ'],
    'ㅁ': CHOSUNG_BRAILLE['ㅁ'],
    'ㅂ': CHOSUNG_BRAILLE['ㅂ'],
    'ㅈ': CHOSUNG_BRAILLE['ㅈ'],
    'ㅋ': CHOSUNG_BRAILLE['ㅋ'],
    'ㅌ': CHOSUNG_BRAILLE['ㅌ'],
    'ㅍ': CHOSUNG_BRAILLE['ㅍ'],
    'ㅎ': CHOSUNG_BRAILLE['ㅎ'],
}
# 제17항 — 이들은 'ㅏ'를 생략한 약자라, 받침 없이 모음으로 시작하는 음절이
# 이어지면 'ㅏ'를 되살려 적는다. '가'·'사'는 제 점형이 따로 있어 해당하지 않는다.
A_ABBREV_DROPS_VOWEL = frozenset('ㄴㄷㅁㅂㅈㅋㅌㅍㅎ')

# 제15항 — 모음으로 시작하는 약자. 글자 속에 포함될 때에도 이 점형을 쓴다.
VOWEL_ABBREV = {
    ('ㅓ', 'ㄱ'): dots_to_braille('1-4-5-6'),      # 억
    ('ㅓ', 'ㄴ'): dots_to_braille('2-3-4-5-6'),    # 언
    ('ㅓ', 'ㄹ'): dots_to_braille('2-3-4-5'),      # 얼
    ('ㅕ', 'ㄴ'): dots_to_braille('1-6'),          # 연
    ('ㅕ', 'ㄹ'): dots_to_braille('1-2-5-6'),      # 열
    ('ㅕ', 'ㅇ'): dots_to_braille('1-2-4-5-6'),    # 영
    ('ㅗ', 'ㄱ'): dots_to_braille('1-3-4-6'),      # 옥
    ('ㅗ', 'ㄴ'): dots_to_braille('1-2-3-5-6'),    # 온
    ('ㅗ', 'ㅇ'): dots_to_braille('1-2-3-4-5-6'),  # 옹
    ('ㅜ', 'ㄴ'): dots_to_braille('1-2-4-5'),      # 운
    ('ㅜ', 'ㄹ'): dots_to_braille('1-2-3-4-6'),    # 울
    ('ㅡ', 'ㄴ'): dots_to_braille('1-3-5-6'),      # 은
    ('ㅡ', 'ㄹ'): dots_to_braille('2-3-4-6'),      # 을
    ('ㅣ', 'ㄴ'): dots_to_braille('1-2-3-4-5'),    # 인
}
# 겹받침은 낱자로 쪼개 둔다. 제15항의 약자가 첫 낱자를 삼키고 나머지가 받침으로
# 남는 경우가 있다 — 넋은 '억' 약자에 받침 ㅅ, 읊은 '을' 약자에 받침 ㅍ.
JONG_PARTS = {
    'ㄲ': ('ㄱ', 'ㄱ'), 'ㄳ': ('ㄱ', 'ㅅ'), 'ㄵ': ('ㄴ', 'ㅈ'), 'ㄶ': ('ㄴ', 'ㅎ'),
    'ㄺ': ('ㄹ', 'ㄱ'), 'ㄻ': ('ㄹ', 'ㅁ'), 'ㄼ': ('ㄹ', 'ㅂ'), 'ㄽ': ('ㄹ', 'ㅅ'),
    'ㄾ': ('ㄹ', 'ㅌ'), 'ㄿ': ('ㄹ', 'ㅍ'), 'ㅀ': ('ㄹ', 'ㅎ'), 'ㅄ': ('ㅂ', 'ㅅ'),
}

# 제16항 — '성, 썽, 정, 쩡, 청'은 첫소리 다음에 '영'의 약자를 적는다. 모음이 ㅓ인데
# ㅕ의 약자를 쓰는 자리라 제15항으로는 잡히지 않는다.
YEONG_CONSONANTS = frozenset(('ㅅ', 'ㅆ', 'ㅈ', 'ㅉ', 'ㅊ'))

# 제12·15항 — 첫소리까지 품은 유일한 약자. 두 칸을 쓴다.
GEOT_ABBREV = dots_to_braille('4-5-6') + dots_to_braille('2-3-4')

# 제14항 — '까·싸·껏'은 약자에 된소리 표를 덧붙인다.
TENSE_MARK = dots_to_braille('6')

# 제14항 — 된소리는 된소리 표를 앞세우고 평음의 약자를 적는다. '까·싸'만 규정에
# 예시가 있지만 '따·빠·짜'도 같은 꼴이다.
TENSE_BASE = {'ㄲ': 'ㄱ', 'ㄸ': 'ㄷ', 'ㅃ': 'ㅂ', 'ㅆ': 'ㅅ', 'ㅉ': 'ㅈ'}

# 받침 ㅆ의 점형은 모음 'ㅖ'와 같다. 'ㅏ'를 생략하면 그 자리가 모음으로 읽히므로
# 제17항이 말하는 "뒤에 모음이 이어 나올 때"에 해당한다 — 팠다, 갔다.
JONG_READS_AS_VOWEL = frozenset(('ㅆ',))

# 제18항 — 약어. 뒤에 다른 음절이 붙어도 쓰지만, 앞에 붙으면 쓰지 않는다.
WORD_ABBREV = {
    '그래서': dots_to_braille('1') + dots_to_braille('2-3-4'),
    '그러나': dots_to_braille('1') + dots_to_braille('1-4'),
    '그러면': dots_to_braille('1') + dots_to_braille('2-5'),
    '그러므로': dots_to_braille('1') + dots_to_braille('2-6'),
    '그런데': dots_to_braille('1') + dots_to_braille('1-3-4-5'),
    '그리고': dots_to_braille('1') + dots_to_braille('1-3-6'),
    '그리하여': dots_to_braille('1') + dots_to_braille('1-5-6'),
}
_WORD_ABBREV_ORDER = sorted(WORD_ABBREV, key=len, reverse=True)


def _syllable_cells(cho: str, jung: str, jong: str, *, keep_a: bool) -> str:
    """One Hangul syllable in cells, 약자와 제2항을 적용해서."""
    # 제14항 — 된소리 약자
    if (cho, jung, jong) == ('ㄲ', 'ㅓ', 'ㅅ'):
        return TENSE_MARK + GEOT_ABBREV
    if (cho, jung, jong) == ('ㄱ', 'ㅓ', 'ㅅ'):
        return GEOT_ABBREV

    out = []
    tense = ''
    base = cho
    if cho in TENSE_BASE and jung == 'ㅏ':
        tense, base = TENSE_MARK, TENSE_BASE[cho]

    # 제12·13·17항 — 'ㅏ' 약자
    if jung == 'ㅏ' and base in A_ABBREV and not (keep_a and base in A_ABBREV_DROPS_VOWEL):
        out.append(tense + A_ABBREV[base])
        if jong:
            out.append(JONGSUNG_BRAILLE[jong])
        return ''.join(out)

    # 제2항 — 첫소리 'ㅇ'은 적지 않는다
    if cho != 'ㅇ':
        out.append(CHOSUNG_BRAILLE[cho])

    # 제16항 — 성·썽·정·쩡·청. 그 대신 이들 뒤의 '셩·졍'은 약자로 적지 않는다.
    if cho in YEONG_CONSONANTS and jong == 'ㅇ':
        if jung == 'ㅓ':
            out.append(VOWEL_ABBREV[('ㅕ', 'ㅇ')])
            return ''.join(out)
        if jung == 'ㅕ':
            out.append(JUNGSUNG_BRAILLE[jung])
            out.append(JONGSUNG_BRAILLE[jong])
            return ''.join(out)

    # 제15항 — 모음으로 시작하는 약자. 겹받침이면 첫 낱자까지만 삼킨다.
    abbrev = VOWEL_ABBREV.get((jung, jong))
    if abbrev is not None:
        out.append(abbrev)
        return ''.join(out)
    head, tail = JONG_PARTS.get(jong, ('', ''))
    abbrev = VOWEL_ABBREV.get((jung, head)) if head else None
    if abbrev is not None:
        out.append(abbrev)
        out.append(JONGSUNG_BRAILLE[tail])
        return ''.join(out)

    out.append(JUNGSUNG_BRAILLE[jung])
    if jong:
        out.append(JONGSUNG_BRAILLE[jong])
    return ''.join(out)


def _continues_number(text: str, index: int) -> bool:
    """제39·49항 — 앞의 숫자와 부호로 이어진 숫자인지. 그러면 수표를 다시 적지 않는다."""
    if index < 2:
        return False
    return text[index - 1] in NUMBER_CONNECTORS and text[index - 2].isdigit()


def _keeps_a_vowel(text: str, index: int) -> bool:
    """제17항 — 받침 없는 'ㅏ' 약자 뒤에 모음으로 시작하는 음절이 한 어절 안에서
    이어지면 'ㅏ'를 생략하지 않는다."""
    nxt = decompose_hangul(text[index + 1]) if index + 1 < len(text) else None
    return nxt is not None and nxt[0] == 'ㅇ'


def _jong_reads_as_vowel(jong: str) -> bool:
    return jong in JONG_READS_AS_VOWEL


def _word_abbrev_at(text: str, index: int) -> tuple[str, int] | None:
    """제18항 — 어절 첫머리에 오는 약어."""
    if index and decompose_hangul(text[index - 1]) is not None:
        return None
    for word in _WORD_ABBREV_ORDER:
        if text.startswith(word, index):
            return WORD_ABBREV[word], len(word)
    return None


# ============================================================
# Main encoder
# ============================================================

def encode_korean_braille(text: str) -> str:
    """Encode Korean text to Korean braille (Unicode)."""
    result = []
    in_number = False
    in_latin = False
    roman_end = -1
    roman_terminated = False
    skip_until = 0

    index = -1
    for ch in text:
        index += 1

        if in_latin and index >= roman_end:
            if roman_terminated:
                result.append(KO_ROMAN_TERMINATOR)
            in_latin = False

        if ch == ' ':
            result.append('\u2800')
            in_number = False
            continue

        if ch == '\n':
            result.append('\n')
            in_number = False
            in_latin = False
            continue

        if index < skip_until:
            continue

        after_number = in_number

        # Hangul syllable
        decomposed = decompose_hangul(ch)
        if decomposed:
            in_number = False
            in_latin = False

            abbrev = _word_abbrev_at(text, index)
            if abbrev is not None:
                result.append(abbrev[0])
                skip_until = index + abbrev[1]
                continue

            cho, jung, jong = decomposed
            prev = decompose_hangul(text[index - 1]) if index else None
            if _needs_link_mark(prev, decomposed):
                result.append(LINK_MARK)
            cells = _syllable_cells(
                    cho,
                    jung,
                    jong,
                    keep_a=_jong_reads_as_vowel(jong)
                    or _continues_number(text, index)
                    or (not jong and _keeps_a_vowel(text, index)),
            )
            # 제38항 [다만] — 숫자 뒤에 숫자와 같은 칸이 이어지면 한 칸 띄운다.
            if after_number and cells[:1] and cells[0] in DIGIT_LOOKALIKE_CELLS:
                result.append('\u2800')
            result.append(cells)
            continue

        # Digit
        if ch.isdigit():
            if not in_number:
                if not _continues_number(text, index):
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
                result.append(KO_ROMAN_INDICATOR)
                in_latin = True
                roman_end = _roman_span_end(text, index)
                roman_terminated = _roman_terminator_needed(text, roman_end)
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

        # Punctuation. 로마자 구간 안의 쉼표·빗금 따위는 구간을 끊지 않는다
        # (제32항) — 구간의 끝은 위에서 roman_end로 이미 정해 두었다.
        in_number = False
        if ch in KO_PUNCT_BRAILLE:
            result.append(KO_PUNCT_BRAILLE[ch])
            continue

        # Other — pass through
        result.append(ch)

    # 본문이 로마자로 끝나면 종료표를 붙일 자리가 루프 안에 남지 않는다.
    if in_latin and roman_terminated:
        result.append(KO_ROMAN_TERMINATOR)

    return ''.join(result)

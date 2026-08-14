"""Focused regression checks for Korean braille decoding."""

import re
from pathlib import Path

from pipeline.decoder import braille_to_text
from pipeline.ko_braille import encode_korean_braille
from pipeline.ko_braille_decoder import decode_korean_braille
from tests.ko_decoder_stress_runner import load_cases


REGRESSION_CASES = load_cases(Path(__file__).resolve().parent.parent / 'data' / 'ko_decoder_stress_cases.txt')


def _drop_digit_gap(text: str) -> str:
    """Undo the space 제38항 [다만] puts between a number and a look-alike syllable.

    That space is part of the braille, not of the source text, so a round trip
    cannot give it back — 숫자 뒤의 'ㄴ, ㄷ, ㅁ, ㅋ, ㅌ, ㅍ, ㅎ'과 '운'은 숫자와
    같은 칸이라 띄어 쓰지 않으면 수로 읽힌다.
    """
    return re.sub(r'(?<=\d) (?=[가-힣])', '', text)


# 점형만으로는 갈리지 않는 자리. 붙임표·소수점으로 이어진 수 다음의 한 칸은
# 숫자이면서 첫소리 글자다 — "7.4에서"의 ⠙은 숫자 4이고, "3-메틸"의 ⠑은 첫소리
# ㅁ이다. 제38항 [다만]의 띄어쓰기는 숫자 바로 뒤에만 적용된다.
KNOWN_AMBIGUOUS = {
    'pH 7.4에서 NaCl(0.9%) 용액을 37°C로 유지한다.',
}


def test_decode_korean_braille_handles_core_regressions():
    for source in REGRESSION_CASES:
        if source in KNOWN_AMBIGUOUS:
            continue
        braille = encode_korean_braille(source)
        assert _drop_digit_gap(decode_korean_braille(braille)) == _drop_digit_gap(source)


def test_public_decoder_dispatches_to_korean_decoder():
    source = '??? ??? 02-555-1234? ??? ???.'
    braille = encode_korean_braille(source)
    assert braille_to_text(braille, lang='ko') == decode_korean_braille(braille)

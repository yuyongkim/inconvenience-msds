"""Pytest sanity checks for round-trip decoder dispatch."""

from pipeline.decoder import braille_to_text
from pipeline.ko_braille_decoder import decode_korean_braille

from tests.roundtrip_harness import decode_braille, encode_braille


def test_ko_roundtrip_uses_korean_decoder_path():
    source = "이것은 간단한 문장입니다."
    braille = encode_braille(source, lang='ko')
    assert decode_braille(braille, lang='ko') == decode_korean_braille(braille)


def test_en_roundtrip_uses_generic_decoder_path():
    source = "This is a simple sentence."
    braille = encode_braille(source, lang='en')
    assert decode_braille(braille, lang='en') == braille_to_text(braille, lang='en')

"""
BRF (Braille Ready Format) ASCII-to-Braille mapping tables.

North American standard: each ASCII character (0x20-0x7E) maps to a braille cell.
In BRF files, uppercase letters are represented by the comma prefix (,) + lowercase.
"""

# ASCII character -> Unicode braille cell
ASCII_TO_BRAILLE = {
    ' ':  '\u2800',  # ⠀ no dots
    '!':  '\u282E',  # ⠮ dots 2-3-4-6
    '"':  '\u2810',  # ⠐ dot 5
    '#':  '\u283C',  # ⠼ dots 3-4-5-6  (number indicator)
    '$':  '\u282B',  # ⠫ dots 1-2-4-6
    '%':  '\u2829',  # ⠩ dots 1-4-6
    '&':  '\u282F',  # ⠯ dots 1-2-3-4-6
    "'":  '\u2804',  # ⠄ dot 3
    '(':  '\u2837',  # ⠷ dots 1-2-3-5-6
    ')':  '\u283E',  # ⠾ dots 2-3-4-5-6
    '*':  '\u2821',  # ⠡ dots 1-6
    '+':  '\u282C',  # ⠬ dots 3-4-6
    ',':  '\u2820',  # ⠠ dot 6  (capital indicator in UEB context)
    '-':  '\u2824',  # ⠤ dots 3-6
    '.':  '\u2828',  # ⠨ dots 4-6
    '/':  '\u280C',  # ⠌ dots 3-4
    '0':  '\u281A',  # ⠚ dots 2-4-5
    '1':  '\u2801',  # ⠁ dot 1
    '2':  '\u2803',  # ⠃ dots 1-2
    '3':  '\u2809',  # ⠉ dots 1-4
    '4':  '\u2819',  # ⠙ dots 1-4-5
    '5':  '\u2811',  # ⠑ dots 1-5
    '6':  '\u280B',  # ⠋ dots 1-2-4
    '7':  '\u281B',  # ⠛ dots 1-2-4-5
    '8':  '\u2813',  # ⠓ dots 1-2-5
    '9':  '\u280A',  # ⠊ dots 2-4
    ':':  '\u2831',  # ⠱ dots 1-5-6
    ';':  '\u2830',  # ⠰ dots 5-6
    '<':  '\u2823',  # ⠣ dots 1-2-6
    '=':  '\u2836',  # ⠶ dots 2-3-5-6
    '>':  '\u281C',  # ⠜ dots 3-4-5
    '?':  '\u2839',  # ⠹ dots 1-4-5-6
    '@':  '\u2808',  # ⠈ dot 4
}

# Lowercase letters a-z
for i, ch in enumerate('abcdefghijklmnopqrstuvwxyz'):
    # Braille letters: a=⠁(dot1), b=⠃(dots12), c=⠉(dots14), ...
    _dots = [
        0x01, 0x03, 0x09, 0x19, 0x11, 0x0B, 0x1B, 0x13, 0x0A, 0x1A,
        0x05, 0x07, 0x0D, 0x1D, 0x15, 0x0F, 0x1F, 0x17, 0x0E, 0x1E,
        0x25, 0x27, 0x3A, 0x2D, 0x3D, 0x35,
    ]
    ASCII_TO_BRAILLE[ch] = chr(0x2800 + _dots[i])

# UEB-specific Unicode braille cells that don't appear in the BRF ASCII table
# but are used in Unicode braille text files.
UEB_UNICODE_EXTRAS = {
    '\u2832': '.',   # ⠲ dots 2-5-6 = UEB period/full stop
    '\u2812': ':',   # ⠒ dots 2-5 = UEB colon
    '\u2822': ',',   # ⠢ dots 2-6 = UEB comma (sometimes)
    '\u2826': '?',   # ⠦ dots 2-3-6 = UEB question mark (opening)
    '\u2816': '!',   # ⠖ dots 2-3-5 = UEB exclamation mark
    '\u2834': '!',   # ⠴ dots 3-5-6 = UEB exclamation (alt)
    '\u2830': ';',   # ⠰ dots 5-6 = semicolon
}

# Reverse mapping: Unicode braille -> ASCII
BRAILLE_TO_ASCII = {v: k for k, v in ASCII_TO_BRAILLE.items()}
# Add UEB extras (these override if there's a conflict, which is fine for decoding)
BRAILLE_TO_ASCII.update(UEB_UNICODE_EXTRAS)

# Number indicator
NUMBER_INDICATOR = '#'
NUMBER_INDICATOR_BRAILLE = '\u283C'

# Capital indicator (in BRF, comma before a letter = capital)
CAPITAL_INDICATOR = ','
CAPITAL_INDICATOR_BRAILLE = '\u2820'

# Letters that follow number indicator map to digits
LETTER_TO_DIGIT = {
    'a': '1', 'b': '2', 'c': '3', 'd': '4', 'e': '5',
    'f': '6', 'g': '7', 'h': '8', 'i': '9', 'j': '0',
}
DIGIT_TO_LETTER = {v: k for k, v in LETTER_TO_DIGIT.items()}

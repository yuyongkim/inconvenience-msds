"""Fig. 2 - Worked Korean braille encoding examples.

Dot patterns are read straight out of the released encoder so the figure can
never drift from the implementation it illustrates.
"""
import sys
from pathlib import Path

from matplotlib.patches import Circle, Rectangle

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from pipeline.ko_braille import (A_ABBREV, CHOSUNG_BRAILLE,  # noqa: E402
                                 GEOT_ABBREV, JONGSUNG_BRAILLE, JUNGSUNG_BRAILLE,
                                 JONGSUNG_LIST, JUNGSUNG_LIST,
                                 TENSE_BASE, TENSE_MARK, VOWEL_ABBREV,
                                 decompose_hangul, encode_korean_braille)

from figstyle import (BORDER, INK, JAMO_BLUE, W_BOLD, W_XBOLD,  # noqa: E402
                      DPI_LINE, blank_canvas, save)

WORDS = ["메탄올", "인화성"]

H_IN = 3.25
fig, ax = blank_canvas(H_IN)
TOP = 100 * H_IN / 6.0

LABEL_X = 10.5
BOX_X0, BOX_W, BOX_GAP = 13.0, 27.0, 2.5
BOX_H = 8.6
DOT_R, DOT_DX, DOT_DY, CELL_ADV = 0.72, 2.25, 2.25, 7.4
GROUP_H = 27.0        # title + syllable boxes + braille row


def cells_for(syllable):
    """(label, braille char) pairs, one per emitted cell.

    Labels follow what the encoder actually writes, so the figure cannot drift
    from `pipeline/ko_braille.py`: 첫소리 'ㅇ'은 적지 않고(제2항), 'ㅏ'가 붙은
    음절과 모음으로 시작하는 음절은 약자 한 칸으로 적는다(제12·15항).
    """
    cho, jung, jong = decompose_hangul(syllable)
    cells = encode_korean_braille(syllable)
    parts: list[tuple[str, str]] = []
    cursor = 0

    def take(seq, label):
        nonlocal cursor
        if seq and cells.startswith(seq, cursor):
            for offset, cell in enumerate(seq):
                parts.append((label if offset == 0 else "", cell))
            cursor += len(seq)
            return True
        return False

    if take(GEOT_ABBREV, syllable):                      # 제12항 '것'
        return parts

    base = cho
    if cho in TENSE_BASE and take(TENSE_MARK, "된소리"):   # 제14항
        base = TENSE_BASE[cho]

    if jung == "ㅏ" and take(A_ABBREV.get(base, ""), syllable):
        take(JONGSUNG_BRAILLE.get(jong, ""), jong)       # 제13항
        return parts

    take(CHOSUNG_BRAILLE.get(base, ""), base)            # 제2항: 'ㅇ'이면 넘어간다

    # 제16항 — '성·썽·정·쩡·청'은 첫소리 뒤에 '영'의 약자를 적는다.
    abbrev_key = ("ㅕ", "ㅇ") if (jung, jong) == ("ㅓ", "ㅇ") and base in "ㅅㅈㅊ" else (jung, jong)
    abbrev_name = chr(0xAC00 + (11 * 21 + JUNGSUNG_LIST.index(abbrev_key[0])) * 28
                      + JONGSUNG_LIST.index(abbrev_key[1]))
    if take(VOWEL_ABBREV.get(abbrev_key, ""), abbrev_name):
        return parts                                      # 제15·16항

    take(JUNGSUNG_BRAILLE.get(jung, ""), jung)
    take(JONGSUNG_BRAILLE.get(jong, ""), jong)
    return parts


def draw_cell(x, y, braille_char):
    """A 2x3 braille cell; raised dots filled, unused positions hollow."""
    bits = ord(braille_char) - 0x2800
    for col in range(2):
        for row in range(3):
            dot = col * 3 + row              # dots 1-3 left column, 4-6 right
            on = bits & (1 << dot)
            ax.add_patch(Circle((x + col * DOT_DX, y - row * DOT_DY), DOT_R,
                                facecolor=INK if on else "white",
                                edgecolor=INK if on else "#B4B4B4",
                                linewidth=0.45, zorder=3))


for g, word in enumerate(WORDS):
    top = TOP - 2.0 - g * GROUP_H
    ax.text(BOX_X0 + 1.0, top, f'"{word}"', ha="left", va="top",
            fontsize=9.5, weight=W_XBOLD, color=INK)

    box_top = top - 5.0
    box_bot = box_top - BOX_H
    ax.text(LABEL_X, box_top - BOX_H * 0.27, "글자:", ha="right", va="center",
            fontsize=6.6, color=INK)
    ax.text(LABEL_X, box_top - BOX_H * 0.74, "자모·약자:", ha="right", va="center",
            fontsize=6.6, color=JAMO_BLUE)
    ax.text(LABEL_X, box_bot - 5.6, "점자:", ha="right", va="center",
            fontsize=6.6, color=INK)

    for i, syllable in enumerate(word):
        x0 = BOX_X0 + i * (BOX_W + BOX_GAP)
        pairs = cells_for(syllable)
        ax.add_patch(Rectangle((x0, box_bot), BOX_W, BOX_H, facecolor="white",
                               edgecolor=BORDER, linewidth=0.7, zorder=2))
        ax.text(x0 + 2.2, box_top - BOX_H * 0.27, syllable, ha="left",
                va="center", fontsize=10.5, color=INK, zorder=3)

        span = (len(pairs) - 1) * (CELL_ADV * 0.72)
        for j, (jamo, _) in enumerate(pairs):
            ax.text(x0 + 3.0 + j * (CELL_ADV * 0.72), box_top - BOX_H * 0.74,
                    jamo, ha="center", va="center", fontsize=7.6,
                    color=JAMO_BLUE, zorder=3)

        cy = box_bot - 4.0
        for j, (_, braille) in enumerate(pairs):
            draw_cell(x0 + 2.0 + j * CELL_ADV, cy, braille)

save(fig, "Fig2", DPI_LINE)

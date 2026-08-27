"""Fig 2 — Korean braille encoding worked examples. Two output sets:
  English row labels  → fig_encoding_example.{pdf,png}     (main.tex)
  Korean row labels   → fig_encoding_example_ko.{pdf,png}  (main_ko.tex)
The example tokens 메탄올 / 인화성 are intentionally Korean (they are the input
to the encoder); only the row labels (Syllable / Jamo / Braille) are translated.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm

ROOT = Path(r"C:\Users\USER\Desktop\Braille")
sys.path.insert(0, str(ROOT))
from pipeline.ko_braille import encode_korean_braille

OUT_DIR = ROOT / "paper" / "archive" / "tex_source"

KOR_FONT = r"C:\Users\USER\AppData\Local\Microsoft\Windows\Fonts\NanumSquareNeo-bRg.ttf"
fm.fontManager.addfont(KOR_FONT)
KOR_FAMILY = fm.FontProperties(fname=KOR_FONT).get_name()


def decompose(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0xAC00 <= o <= 0xD7A3:
            idx = o - 0xAC00
            cho_i = idx // 588
            jung_i = (idx % 588) // 28
            jong_i = idx % 28
            CHO = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")
            JUNG = list("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ")
            JONG = [""] + list("ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ")
            out.append((ch, CHO[cho_i], JUNG[jung_i], JONG[jong_i]))
        else:
            out.append((ch, ch, "", ""))
    return out


def braille_cells(s):
    return [c for c in encode_korean_braille(s) if 0x2800 <= ord(c) <= 0x28FF]


def cell_dots(c):
    bits = ord(c) - 0x2800
    return [(i + 1) for i in range(6) if bits & (1 << i)]


def draw_braille_cell(ax, x, y, dots, size=0.25):
    for slot in range(1, 7):
        row = (slot - 1) % 3
        col = (slot - 1) // 3
        cx = x + col * size * 0.6
        cy = y - row * size * 0.6
        if slot in dots:
            ax.add_patch(patches.Circle((cx, cy), size * 0.18, color="#222222"))
        else:
            ax.add_patch(patches.Circle((cx, cy), size * 0.18,
                                        fill=False, edgecolor="#bbbbbb", linewidth=0.7))


def render(lang: str, out_stem: str):
    is_ko = lang == "ko"
    # use Korean font for both because the example tokens (메탄올·인화성) are Korean
    plt.rcParams["font.family"] = KOR_FAMILY
    plt.rcParams["axes.unicode_minus"] = False

    if is_ko:
        title = "Fig. 2. 한국 점자 인코딩: 음절 → 자모 분해 → 점자 셀"
        row_syl = "글자:"
        row_jamo = "자모:"
        row_braille = "점자:"
    else:
        title = "Fig. 2. Korean braille encoding: syllable → jamo decomposition → braille cells"
        row_syl = "Syllable:"
        row_jamo = "Jamo:"
        row_braille = "Braille:"

    fig, ax = plt.subplots(figsize=(11, 5.0))
    ax.set_xlim(0, 13)
    ax.set_ylim(-2.5, 4.5)
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10)

    def draw_example(word, x_origin, y_origin):
        decomposed = decompose(word)
        cells = braille_cells(word)
        ax.text(x_origin, y_origin + 1.4, f"\"{word}\"", fontsize=18, fontweight="bold")

        syl_x = x_origin
        cell_idx = 0
        for ch, cho, jung, jong in decomposed:
            n_jamo = sum(1 for j in (cho, jung, jong) if j)
            block_w = max(1.2, n_jamo * 0.95)
            ax.add_patch(patches.Rectangle((syl_x, y_origin - 0.05), block_w, 0.95,
                                           fill=False, edgecolor="#999", linewidth=0.8))
            ax.text(syl_x + 0.15, y_origin + 0.7, ch, fontsize=18)
            jx = syl_x + 0.15
            for j in (cho, jung, jong):
                if not j:
                    continue
                ax.text(jx, y_origin + 0.15, j, fontsize=14, color="#1565C0")
                jx += 0.4
            for k in range(n_jamo):
                if cell_idx < len(cells):
                    draw_braille_cell(ax, syl_x + 0.1 + k * 0.55, y_origin - 0.5,
                                      cell_dots(cells[cell_idx]))
                    cell_idx += 1
            syl_x += block_w + 0.2

        while cell_idx < len(cells):
            draw_braille_cell(ax, syl_x, y_origin - 0.5, cell_dots(cells[cell_idx]))
            syl_x += 0.55
            cell_idx += 1

        # row labels
        ax.text(x_origin - 0.5, y_origin + 0.7, row_syl,
                fontsize=11, color="#444", ha="right")
        ax.text(x_origin - 0.5, y_origin + 0.15, row_jamo,
                fontsize=11, color="#1565C0", ha="right")
        ax.text(x_origin - 0.5, y_origin - 0.5, row_braille,
                fontsize=11, color="#222", ha="right")

    draw_example("메탄올", 1.6, 2.8)
    draw_example("인화성", 1.6, -0.4)

    fig.tight_layout()
    pdf = OUT_DIR / f"{out_stem}.pdf"
    png = OUT_DIR / f"{out_stem}.png"
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(png, bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"Wrote {pdf} and {png}")


render("en", "fig_encoding_example")
render("ko", "fig_encoding_example_ko")

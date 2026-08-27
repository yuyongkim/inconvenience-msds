"""Fig 3 — Dataset characteristics. Two output sets:
  English labels  → fig_dataset_stats.{pdf,png}     (used by main.tex)
  Korean labels   → fig_dataset_stats_ko.{pdf,png}  (used by main_ko.tex)
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

ROOT = Path(r"C:\Users\USER\Desktop\Braille")
JSONL = ROOT / "data" / "hf_dataset" / "train.jsonl"
OUT_DIR = ROOT / "paper" / "archive" / "tex_source"

KOR_FONT = r"C:\Users\USER\AppData\Local\Microsoft\Windows\Fonts\NanumSquareNeo-bRg.ttf"
fm.fontManager.addfont(KOR_FONT)
KOR_FAMILY = fm.FontProperties(fname=KOR_FONT).get_name()

ko = la = di = 0
text_lengths = []
with open(JSONL, "r", encoding="utf-8") as f:
    for line in f:
        d = json.loads(line)
        text_lengths.append(d["total_text_chars"])
        for s in d["sections"]:
            for c in (s.get("text_ko") or ""):
                o = ord(c)
                if 0xAC00 <= o <= 0xD7A3:
                    ko += 1
                elif (0x41 <= o <= 0x5A) or (0x61 <= o <= 0x7A):
                    la += 1
                elif "0" <= c <= "9":
                    di += 1

total = ko + la + di
ko_pct = 100 * ko / total
la_pct = 100 * la / total
di_pct = 100 * di / total

arr = np.array(text_lengths)
mean = arr.mean()
median = float(np.median(arr))
std = arr.std()
mn, mx = arr.min(), arr.max()


def render(lang: str, out_stem: str):
    is_ko = lang == "ko"
    plt.rcParams["font.family"] = KOR_FAMILY if is_ko else "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    if is_ko:
        labels = ["한국어", "라틴", "숫자"]
        ax1_title = "(a) 문자 분포 (한국어 / 라틴 / 숫자)"
        x_label = "화학물질당 총 한국어 텍스트 길이 (문자 수)"
        y_label = "화학물질 수"
        ax2_title = "(b) 화학물질당 텍스트 길이 분포"
        mean_lbl = f"평균 = {mean:.0f}"
        med_lbl = f"중앙값 = {median:.0f}"
        stats_text = (
            f"평균 = {mean:.0f}\n"
            f"중앙값 = {median:.0f}\n"
            f"표준편차 = {std:.0f}\n"
            f"최소 / 최대 = {mn} / {mx}\n"
            f"n = {len(arr):,}"
        )
    else:
        labels = ["Korean", "Latin", "Digits"]
        ax1_title = "(a) Character type distribution"
        x_label = "Total Korean text length per chemical (chars)"
        y_label = "Chemicals (records)"
        ax2_title = "(b) Per-chemical text length distribution"
        mean_lbl = f"mean = {mean:.0f}"
        med_lbl = f"median = {median:.0f}"
        stats_text = (
            f"mean = {mean:.0f}\n"
            f"median = {median:.0f}\n"
            f"std = {std:.0f}\n"
            f"min / max = {mn} / {mx}\n"
            f"n = {len(arr):,}"
        )

    sizes = [ko_pct, la_pct, di_pct]
    colors = ["#4285F4", "#EA4335", "#FBBC04"]
    explode = (0.03, 0.03, 0.03)
    wedges, texts, autotexts = ax1.pie(
        sizes, labels=labels, autopct="%1.1f%%", startangle=140,
        colors=colors, explode=explode, textprops={"fontsize": 11},
        pctdistance=0.55,
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight("bold")
    ax1.set_title(ax1_title, fontsize=13, fontweight="bold", pad=12)

    ax2.hist(arr, bins=60, color="#4285F4", edgecolor="white", alpha=0.85)
    ax2.axvline(mean, color="#EA4335", linestyle="--", linewidth=1.8, label=mean_lbl)
    ax2.axvline(median, color="#34A853", linestyle=":", linewidth=1.8, label=med_lbl)
    ax2.set_xlabel(x_label, fontsize=11)
    ax2.set_ylabel(y_label, fontsize=11)
    ax2.set_title(ax2_title, fontsize=13, fontweight="bold", pad=12)
    ax2.legend(fontsize=9)

    ax2.text(0.97, 0.95, stats_text, transform=ax2.transAxes,
             fontsize=9, verticalalignment="top", horizontalalignment="right",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFF3E0", alpha=0.9))

    fig.tight_layout(pad=1.5)
    pdf = OUT_DIR / f"{out_stem}.pdf"
    png = OUT_DIR / f"{out_stem}.png"
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(png, bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"Wrote {pdf} and {png}")


render("en", "fig_dataset_stats")
render("ko", "fig_dataset_stats_ko")
print(f"Char dist: Korean {ko_pct:.2f}%, Latin {la_pct:.2f}%, Digit {di_pct:.2f}%")
print(f"Stats: mean={mean:.1f}, median={median:.0f}, std={std:.1f}, min={mn}, max={mx}")

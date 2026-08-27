"""Recompute all numerical claims in the paper from data/hf_dataset/train.jsonl."""
import json
import statistics
import sys
import io
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

JSONL = Path(__file__).parent.parent / "data" / "hf_dataset" / "train.jsonl"


def is_hangul(c):
    o = ord(c)
    return 0xAC00 <= o <= 0xD7A3 or 0x1100 <= o <= 0x11FF or 0x3130 <= o <= 0x318F


def is_latin(c):
    o = ord(c)
    return 0x41 <= o <= 0x5A or 0x61 <= o <= 0x7A


def is_digit(c):
    return '0' <= c <= '9'


def is_braille_cell(c):
    o = ord(c)
    return 0x2800 <= o <= 0x28FF


def main():
    n_chems = 0
    n_sections = 0
    section_no_counts = Counter()
    text_lengths = []
    text_total = 0
    braille_total = 0
    ko_count = 0
    la_count = 0
    di_count = 0
    other_count = 0

    with open(JSONL, "r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            n_chems += 1
            secs = d.get("sections", [])
            chem_text_chars = 0
            chem_braille_cells = 0
            for s in secs:
                no = s.get("section_no")
                if no is not None:
                    section_no_counts[no] += 1
                n_sections += 1
                txt = s.get("text_ko") or ""
                br = s.get("braille") or ""
                for c in txt:
                    if is_hangul(c):
                        ko_count += 1
                    elif is_latin(c):
                        la_count += 1
                    elif is_digit(c):
                        di_count += 1
                    else:
                        other_count += 1
                chem_text_chars += len(txt)
                chem_braille_cells += sum(1 for c in br if is_braille_cell(c))
            text_lengths.append(chem_text_chars)
            text_total += chem_text_chars
            braille_total += chem_braille_cells
            if n_chems % 5000 == 0:
                print(f"  ...{n_chems} chemicals processed", file=sys.stderr, flush=True)

    text_lengths.sort()
    n = len(text_lengths)
    mean_text = text_total / n
    median_text = text_lengths[n // 2] if n % 2 == 1 else (text_lengths[n // 2 - 1] + text_lengths[n // 2]) / 2
    std_text = statistics.pstdev(text_lengths)
    min_text = text_lengths[0]
    max_text = text_lengths[-1]
    ratio = braille_total / text_total

    classified = ko_count + la_count + di_count
    ko_pct = 100.0 * ko_count / classified
    la_pct = 100.0 * la_count / classified
    di_pct = 100.0 * di_count / classified

    print("\n=== AUTHORITATIVE RECOMPUTE ===")
    print(f"Total chemicals       : {n_chems:,}")
    print(f"Total sections        : {n_sections:,}")
    print(f"Sections per section# : {dict(sorted(section_no_counts.items()))}")
    print(f"Korean text total     : {text_total:,} chars  ({text_total/1e6:.2f} M)")
    print(f"Braille cells total   : {braille_total:,} cells ({braille_total/1e6:.2f} M)")
    print(f"Avg text per chem     : {mean_text:.1f}")
    print(f"Median text per chem  : {median_text:.1f}")
    print(f"Std dev               : {std_text:.1f}")
    print(f"Min / Max text        : {min_text} / {max_text}")
    print(f"Braille:text ratio    : {ratio:.3f}")
    print(f"Char distribution (classified Hangul/Latin/Digit only):")
    print(f"  Korean   : {ko_count:,}  ({ko_pct:.2f}%)")
    print(f"  Latin    : {la_count:,}  ({la_pct:.2f}%)")
    print(f"  Digit    : {di_count:,}  ({di_pct:.2f}%)")
    print(f"  (other punctuation/space ignored: {other_count:,})")

    out = {
        "total_chemicals": n_chems,
        "total_sections": n_sections,
        "section_no_counts": dict(sorted(section_no_counts.items())),
        "korean_text_chars_total": text_total,
        "braille_cells_total": braille_total,
        "avg_text_per_chem": mean_text,
        "median_text_per_chem": median_text,
        "std_text_per_chem": std_text,
        "min_text": min_text,
        "max_text": max_text,
        "braille_text_ratio": ratio,
        "char_distribution_classified": {
            "korean": ko_count,
            "latin": la_count,
            "digit": di_count,
            "korean_pct": ko_pct,
            "latin_pct": la_pct,
            "digit_pct": di_pct,
        },
        "other_chars_ignored": other_count,
    }
    out_path = Path(__file__).parent / "verified_numbers.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()

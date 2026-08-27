"""Re-run the cross-reference validation: encode KR text with our encoder
and the independent hbcvt (hangul-braille-converter) and count agreement.

Builds three test sets:
  (a) Basic Hangul syllables  — randomly sampled 41 unique syllables
  (b) Korean golden sentences — from data/golden_braille_roundtrip_ko.csv (45 rows)
  (c) MSDS chemical names      — 356 unique Korean names from the DB

Reports per-set agreement %.

Note: hbcvt operates on plain Hangul-only text; our encoder is mixed-script
aware. To make the comparison apples-to-apples we strip non-Hangul/space from
inputs before passing to either side, matching the original validation harness
behavior referenced in the paper.
"""
import csv
import io
import sqlite3
import sys
import random
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "data" / "braille" / "ref_converter"))

from pipeline.ko_braille import encode_korean_braille
from hbcvt import h2b as ref


def hangul_only(s: str) -> str:
    return ''.join(ch if (0xAC00 <= ord(ch) <= 0xD7A3 or ch == ' ') else '' for ch in s)


def dots_to_cell(dots) -> str:
    """[d1..d6] → U+2800+bitmask braille cell."""
    bits = 0
    for i, v in enumerate(dots):
        if v:
            bits |= 1 << i
    return chr(0x2800 + bits)


def hbcvt_to_unicode(structured) -> str:
    """Flatten hbcvt.text() output to a Unicode braille string."""
    out = []
    for syl_entry in structured:
        # syl_entry = [syllable_str, [[jamo, [[d1..d6], ...]], ...]]
        jamos = syl_entry[1]
        for jamo_entry in jamos:
            cells = jamo_entry[1]
            for c in cells:
                if all(v == 0 for v in c):
                    out.append(' ')
                else:
                    out.append(dots_to_cell(c))
    return ''.join(out)


def cmp(text: str) -> tuple[str, str, bool]:
    t = hangul_only(text).strip()
    if not t:
        return ("", "", True)
    ours = encode_korean_braille(t)
    theirs_struct = ref.text(t)
    theirs = hbcvt_to_unicode(theirs_struct)
    # normalize: braille blank cell (U+2800) ↔ ASCII space are equivalent spacing
    def _norm(s):
        return ''.join((' ' if c in ('⠀', ' ') else c)
                       for c in s
                       if 0x2800 <= ord(c) <= 0x28FF or c == ' ')
    o = _norm(ours)
    t2 = _norm(theirs)
    return (o, t2, o == t2)


def basic_syllables(n=41, seed=42):
    random.seed(seed)
    chosen = []
    while len(chosen) < n:
        code = 0xAC00 + random.randint(0, 11171)
        ch = chr(code)
        if ch not in chosen:
            chosen.append(ch)
    return chosen


def golden_sentences():
    path = PROJECT_ROOT / "data" / "golden_braille_roundtrip_ko.csv"
    rows = []
    with open(path, encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            # the source column may be 'text' or 'input' or 'ko_text'
            for k in ('source_text', 'text', 'input', 'ko_text', 'source', 'sentence'):
                if k in row and row[k]:
                    rows.append(row[k])
                    break
    return rows


def msds_names(n=356):
    conn = sqlite3.connect("G:/MSDS/data/terminology.db")
    names = []
    for (nm,) in conn.execute(
        "SELECT DISTINCT name FROM chemical_terms WHERE name IS NOT NULL ORDER BY external_id"
    ):
        h = hangul_only(nm).strip()
        if h and len(h) >= 1:
            names.append(nm)
            if len(names) >= n:
                break
    return names


def run_set(label: str, cases: list[str]):
    n = len(cases)
    agree = 0
    disagreements = []
    for t in cases:
        ours, theirs, ok = cmp(t)
        if ok:
            agree += 1
        else:
            if len(disagreements) < 5:
                disagreements.append((t, ours, theirs))
    print(f"\n[{label}]  {agree}/{n}  ({100*agree/n:.1f}%)")
    if disagreements:
        print(f"  first {len(disagreements)} disagreements:")
        for src, a, b in disagreements:
            print(f"    src     : {src!r}")
            print(f"    ours    : {a!r}")
            print(f"    theirs  : {b!r}")
    return agree, n


def main():
    print("=== CROSS-REFERENCE VALIDATION (re-run) ===")

    a1, n1 = run_set("Basic Hangul syllables", basic_syllables(41))
    a2, n2 = run_set("Korean golden sentences", golden_sentences())
    a3, n3 = run_set("MSDS chemical names", msds_names(356))

    total = a1 + a2 + a3
    grand = n1 + n2 + n3
    print(f"\n=== TOTAL ===  {total}/{grand}  ({100*total/grand:.1f}%)")
    print(f"  (paper claim: 41+45+356=442 at 100%)")


if __name__ == "__main__":
    main()

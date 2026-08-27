"""Single pass over the released JSONL to recompute every number Figs 3 and 4 plot."""
import json
from collections import Counter, defaultdict
from pathlib import Path

JSONL = Path(r"C:\Users\USER\Desktop\Braille\data\hf_dataset\train.jsonl")
OUT = Path(__file__).with_name("fig_stats.json")

ko = la = di = 0
braille_cells = 0
text_lengths = []
section_n = Counter()
section_chars_sum = defaultdict(int)
n_chem = 0
nonempty_sections = 0

with JSONL.open("r", encoding="utf-8") as f:
    for line in f:
        d = json.loads(line)
        n_chem += 1
        text_lengths.append(d.get("total_text_chars", 0))
        for s in d["sections"]:
            txt = s.get("text_ko") or ""
            for c in txt:
                o = ord(c)
                if 0xAC00 <= o <= 0xD7A3:
                    ko += 1
                elif (0x41 <= o <= 0x5A) or (0x61 <= o <= 0x7A):
                    la += 1
                elif "0" <= c <= "9":
                    di += 1
            braille_cells += len(s.get("braille") or "")
            no = s.get("section_no")
            if no is not None and txt.strip():
                section_n[no] += 1
                section_chars_sum[no] += len(txt)
                nonempty_sections += 1

import statistics

res = {
    "n_chemicals": n_chem,
    "nonempty_sections": nonempty_sections,
    "braille_cells": braille_cells,
    "char_counts": {"korean": ko, "latin": la, "digits": di},
    "text_len": {
        "mean": statistics.mean(text_lengths),
        "median": statistics.median(text_lengths),
        "std": statistics.pstdev(text_lengths),
        "min": min(text_lengths),
        "max": max(text_lengths),
        "total": sum(text_lengths),
    },
    "section_n": {str(i): section_n[i] for i in range(1, 17)},
    "section_mean_len": {
        str(i): (section_chars_sum[i] / section_n[i]) if section_n[i] else 0.0
        for i in range(1, 17)
    },
    "hist_lengths": text_lengths,
}
OUT.write_text(json.dumps(res), encoding="utf-8")
res.pop("hist_lengths")
print(json.dumps(res, indent=2, ensure_ascii=False))

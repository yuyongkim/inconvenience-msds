# Supplementary Materials — KOSHA-Braille

This package accompanies the manuscript **"KOSHA-Braille: Infrastructure-Grade
Accessibility for Korean Chemical Safety Information"** (Y. Y. Kim).
Every quantitative claim in the manuscript can be regenerated from these files.

## Contents

| File | Purpose | Used by |
|------|---------|---------|
| `verify_numbers.py` | Recompute totals, per-chemical statistics, character-type distribution from the released HuggingFace JSONL (`data/hf_dataset/train.jsonl`). | Abstract; Sec IV-B Table IV; Fig 3. |
| `verify_cross_reference.py` | Re-run the 442-case cross-reference validation against the independent open-source converter `hbcvt` (`hangul-braille-converter`). | Sec V-B Table VI. |
| `verified_numbers.json` | Frozen authoritative output of `verify_numbers.py` at submission time. | All numerical claims about the corpus. |
| `gen_fig_pipeline.py` | Source for Fig 1. | Sec III. |
| `gen_fig_encoding_example.py` | Source for Fig 2 (worked encoding examples for "메탄올" and "인화성"). | Sec III-B. |
| `gen_fig_dataset_stats.py` | Source for Fig 3 (character distribution + per-chemical length histogram, real data). | Sec IV-B. |
| `gen_fig_section_coverage.py` | Source for Fig 4 (per-section coverage and average length). | Sec IV-B. |
| `gen_fig_webui.py` | Source for Fig 5 (web service screenshot). | Sec VI. |
| `golden_braille_roundtrip_ko.csv` | 45-sentence Korean golden set used for round-trip and cross-reference checks. | Sec V; round-trip 45/45 claim. |
| `ko_decoder_stress_cases.txt` | 27-case persistent decoder stress corpus. | Sec V-D. |
| `ghs_summary.json` | GHS H/P statement counts produced by `scripts/ghs_braille.py`. | Sec IV-C (147 codes = 63 H + 84 P). |

## Reproducing the headline numbers

From the project root, with Python 3.10+:

```bash
# (1) Corpus totals, per-chemical stats, character distribution
python paper/supplementary/verify_numbers.py
#   → writes paper/verified_numbers.json
#   → printed: total chemicals, sections, char counts, mean/median/std, ratios

# (2) Cross-reference 442/442 100% agreement
python paper/supplementary/verify_cross_reference.py
#   → prints set-by-set agreement and the 442-case total

# (3) Figures 1–5
python paper/supplementary/gen_fig_pipeline.py
python paper/supplementary/gen_fig_encoding_example.py
python paper/supplementary/gen_fig_dataset_stats.py
python paper/supplementary/gen_fig_section_coverage.py
python paper/supplementary/gen_fig_webui.py
```

Dependencies: `numpy`, `matplotlib`, `lxml`, and the project's own
`pipeline/` package (in particular `pipeline.ko_braille.encode_korean_braille`
and `pipeline.ko_braille_decoder.decode_korean_braille`). The cross-reference
script additionally requires the vendored independent converter at
`data/braille/ref_converter/` (sourced from
`https://github.com/hyonzin/hangul-braille-converter`).

## Authoritative data sources

- KOSHA MSDS corpus: `data/hf_dataset/train.jsonl` (943 MB, 48,966 chemicals,
  401,272 non-empty sections; mirror of HuggingFace release).
- Source SQLite DB: `G:/MSDS/data/terminology.db` (local; reproducible from
  the Korea Public Data Portal API).
- Domain extension exports: `data/domain_expansion/`
  (food_allergens_braille.jsonl, drug_labels_braille.jsonl,
  kischem_firstaid_braille.jsonl).

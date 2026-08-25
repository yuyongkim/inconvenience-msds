# inconvenience-msds

> *Inconvenience #01 — Material Safety Data Sheets in Korean braille*

Accessibility infrastructure for Korean chemical safety information.
48,966 chemicals × up to 16 MSDS sections, encoded as Korean braille
(2017 한국 점자 규정), released as a public dataset, encoder, and reference
web service.

[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![HF Dataset](https://img.shields.io/badge/🤗-dataset-yellow)](https://huggingface.co/datasets/Yuyongkim/inconvenience-msds)
[![DOI](https://img.shields.io/badge/DOI-10.1007%2Fs10209--026--01381--0-blue)](https://doi.org/10.1007/s10209-026-01381-0)

**Live service**: <https://braille.yule.pics>

## Citation

Kim, Y. (2026). KOSHA-Braille: infrastructure-grade accessibility for Korean
chemical safety information. *Universal Access in the Information Society*,
25, 116. https://doi.org/10.1007/s10209-026-01381-0

```bibtex
@article{kim2026koshabraille,
  author  = {Kim, Yuyong},
  title   = {{KOSHA-Braille}: infrastructure-grade accessibility for Korean chemical safety information},
  journal = {Universal Access in the Information Society},
  volume  = {25},
  pages   = {116},
  year    = {2026},
  doi     = {10.1007/s10209-026-01381-0}
}
```

The paper describes **corpus v1.0** (`corpus-v1.0`, 232.3 M braille cells).
Later versions changed the braille after a rule-by-rule audit against the
standard; see `notes/2026-08-13-regulation-audit.md`.

---

## What this is

A working argument that chemical-safety information is **infrastructure-grade
accessibility** — like tactile paving or platform screen doors — and should
exist whether or not anyone asks for it on a given day.

This repository contains:

- **Dataset** — 48,966 chemicals, 769,897 MSDS sections, ~197M braille cells (v1.2; the published report describes v1.0 at ~232M)
- **Encoder** — deterministic Korean text → Korean braille (2017 standards)
- **Decoder** — Korean braille → Korean text (round-trip tooling)
- **Pipeline** — full EN/KR braille conversion pipeline (13 modules)
- **Web service** — FastAPI backend + single-page frontend
- **Paper** — IEEE Access draft (`paper/`)

## The `inconvenience` series

This is the first entry in a planned series of accessibility-infrastructure
projects targeting domains where the visually impaired user population is
small but the consequences of inaccessibility are large. Planned successors:

- `inconvenience-pharmacy` — drug labels and inserts (KMFDS)
- `inconvenience-law` — statutes and administrative rulings
- `inconvenience-emergency` — first-aid and emergency-response protocols

The naming is deliberate: the inconvenience belongs to the user, not the
work. Each entry tries to remove one.

## Quick start

```bash
# Install
pip install -e .

# Convert Korean text to braille
python -c "from pipeline.ko_braille import encode_korean_braille; \
           print(encode_korean_braille('벤젠은 방향족 탄화수소이다.'))"

# Run the web service locally
# - Uses `data/terminology.sample.db` by default (small sample DB included for demo)
# - For full data, set `BRAILLE_MSDS_DB_PATH` to your `terminology.db` path
cd web/backend && uvicorn server:app --port 8000

# Bulk-convert the entire KOSHA database (requires terminology.db)
python scripts/msds_bulk_braille.py

# Re-export the HuggingFace dataset
python scripts/export_hf_dataset.py
```

## Dataset

The full corpus is released on HuggingFace:
**[Yuyongkim/inconvenience-msds](https://huggingface.co/datasets/Yuyongkim/inconvenience-msds)**

```python
from datasets import load_dataset
ds = load_dataset("Yuyongkim/inconvenience-msds", split="train")
print(ds[0]["sections"][0]["braille"])
```

Each record:

```json
{
  "chem_id": "001008",
  "name_ko": "벤젠 (Benzene)",
  "cas_no": "71-43-2",
  "name_en": "Benzene",
  "sections": [
    {
      "section_no": 1,
      "title": "화학제품과 회사에 관한 정보",
      "text_ko": "제품명: 벤젠 ...",
      "braille": "⠨⠝⠙⠍⠢⠑⠱⠶⠐⠂..."
    }
  ],
  "total_text_chars": 6123,
  "total_braille_chars": 11920
}
```

## Output formats

| Format | Use |
|--------|-----|
| Unicode braille (`.txt`, U+2800–U+28FF) | refreshable braille displays, accessible reading software |
| BRF (`.brf`) | braille embossers (40 cells × 25 lines) |
| PDF | sighted-side preview / verification |
| JSONL | dataset / training |

## Validation

- **442 / 442 (100%)** agreement with independent open-source Korean
  braille converter [hangul-braille-converter](https://github.com/hyonzin/hangul-braille-converter)
- **0 errors** across 48,966 chemicals in bulk conversion
- **98.1%** character encoding coverage on 500-sample audit
- Korean round-trip metrics are reported as decoder diagnostics, not encoder-correctness scores; after routing KR evaluation through the Korean decode path and tightening mixed-script/punctuation/number-span handling, the current golden-set round-trip result is **1.000 edit similarity / 1.000 ChrF (45/45)**
- Persistent decoder stress corpus: **39 cases, 1 failure** (`results/ko_decoder_stress_summary.csv`)
- Random sample real-text decoder spot-check: **12 rows across 3 runs, 0 failures** (`results/ko_decoder_realtext_spotcheck_summary.csv`)
- Synthetic noisy-braille stress: at **2% / 5% / 10%** corruption, average edit similarity is **0.8894 / 0.8690 / 0.7558** (`results/ko_decoder_noisy_stress_summary.csv`)
- Encoder audited rule by rule against the 2017 standard on 2026-08-14 — 첫소리 ㅇ 생략(제2항),
  약자·약어(제12~18항), 로마자 종료표(제30항), 괄호 두 칸(제54~56항)을 반영했다.
  남은 미구현 항목은 `notes/2026-08-13-regulation-audit.md`에 정리돼 있다.
- Standards-compliant per 2017 Korean Braille Standards
  ([Notification 2017-15](https://www.law.go.kr), Ministry of Culture, Sports and Tourism)

## Repository layout

```
pipeline/         # 13 modules — encoder, decoder, structure, translator, embosser
scripts/          # bulk conversion, validation, dataset export
eval/             # evaluation harness
tests/            # round-trip and golden-set tests
web/              # FastAPI backend + single-page frontend
data/             # golden sets, reference tables, exported corpora
paper/            # IEEE Access draft (LaTeX + figures)
results/          # bulk conversion outputs, evaluation results
```

See [`CLAUDE.md`](CLAUDE.md) for module-level documentation.
Decoder QA commands and current verification scope are summarized in
[`notes/decoder_qa.md`](notes/decoder_qa.md).
Release-oriented decoder QA signoff is tracked in
[`notes/decoder_release_checklist.md`](notes/decoder_release_checklist.md).
A concise quality split across encoder, decoder, and data is tracked in
[`notes/quality_snapshot.md`](notes/quality_snapshot.md).

## Why this exists

The most common objection to producing domain-specific braille
infrastructure is that the expected user population is small. In Korean
chemical safety the observable population of visually impaired chemists
or chemical-safety regulators is close to zero.

This is not evidence against infrastructure. It is evidence *for* it.
Low observable participation in a profession is a predictable consequence
of inaccessible professional information, not an independent fact about
preference or capability.

The legal basis is already in place:

- **UN CRPD Article 9** (Accessibility) — South Korea ratified 2008
- **장애인차별금지법 제21조** (Information Access)

The infrastructure is what was missing. This repository is a first
contribution toward building it.

## Citation

```bibtex
@article{kim2026inconveniencemsds,
  title={KOSHA-Braille: Infrastructure-Grade Accessibility for Korean
         Chemical Safety Information},
  author={Kim, Yu Yong},
  journal={IEEE Access},
  year={2026},
  note={Submitted}
}
```

## License

- **Code** — [MIT](LICENSE)
- **Dataset** — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Source MSDS data** — Korea Public Data Portal (공공누리 제1유형, 출처표시)

## Acknowledgements

Source data from the Korea Occupational Safety and Health Agency (KOSHA)
via the Korea Public Data Portal. Independent encoder reference:
[hangul-braille-converter](https://github.com/hyonzin/hangul-braille-converter)
by hyonzin and [hanbraille](https://github.com/delvier/hanbraille) by delvier.

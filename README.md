# inconvenience-msds

> *Inconvenience #01 — Material Safety Data Sheets in Korean braille*

Accessibility infrastructure for Korean chemical safety information.
48,966 chemicals × up to 16 MSDS sections, encoded as Korean braille
(2017 한국 점자 규정), released as a public dataset, encoder, and reference
web service.

[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![HF Dataset](https://img.shields.io/badge/🤗-dataset-yellow)](https://huggingface.co/datasets/Yuyongkim/inconvenience-msds)

---

## What this is

A working argument that chemical-safety information is **infrastructure-grade
accessibility** — like tactile paving or platform screen doors — and should
exist whether or not anyone asks for it on a given day.

This repository contains:

- **Dataset** — 48,966 chemicals, 769,897 MSDS sections, ~232M braille cells
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

---
language:
- ko
license: cc-by-4.0
size_categories:
- 10K<n<100K
task_categories:
- translation
- text-generation
tags:
- braille
- accessibility
- chemical-safety
- msds
- korean
- kosha
- ghs
- inconvenience-series
pretty_name: "inconvenience-msds (KOSHA chemical safety in Korean braille)"
dataset_info:
  features:
  - name: chem_id
    dtype: string
  - name: name_ko
    dtype: string
  - name: cas_no
    dtype: string
  - name: name_en
    dtype: string
  - name: sections
    sequence:
      struct:
      - name: section_no
        dtype: int32
      - name: title
        dtype: string
      - name: text_ko
        dtype: string
      - name: braille
        dtype: string
  - name: total_text_chars
    dtype: int32
  - name: total_braille_chars
    dtype: int32
  splits:
  - name: train
    num_examples: 48966
configs:
- config_name: default
  data_files:
  - split: train
    path: train.jsonl
---

# inconvenience-msds

> *Inconvenience #01 — Material Safety Data Sheets in Korean braille*

Accessibility infrastructure for Korean chemical safety information.
**48,966 chemicals × up to 16 MSDS sections**, encoded as Korean braille
following the 2017 한국 점자 규정 (Korean Braille Standards).

## What this is

This dataset is the first entry in the `inconvenience` series — a planned
sequence of accessibility-infrastructure datasets targeting domains where
the visually impaired user population is small but the consequences of
inaccessibility are large.

The most common objection to producing domain-specific braille
infrastructure is that the expected user population is small. We argue
this observation is not evidence against infrastructure but evidence
*for* it: low observable participation in a profession is a predictable
consequence of inaccessible professional information, not an independent
fact about preference or capability. The legal basis for producing this
infrastructure is already in place under UN CRPD Article 9 and Korea's
장애인차별금지법 제21조; what was missing was the artifact itself.

The naming is deliberate: the inconvenience belongs to the user, not the
work. Each entry tries to remove one.

## Quick start

```python
from datasets import load_dataset

ds = load_dataset("Yuyongkim/inconvenience-msds", split="train")
print(ds[0]["name_ko"])
print(ds[0]["sections"][1]["braille"][:200])
```

## Source

Korea Occupational Safety and Health Agency (KOSHA) public MSDS database,
retrieved via the Korea Public Data Portal API (data.go.kr) under an
authorized operational account.

## Versions

The braille side of this corpus changed after a rule-by-rule audit of the encoder
against the source standard. Pin the version you need.

| Version | Encoder | Braille cells | Ratio | File |
|---|---|---|---|---|
| **v1.0** | as described in the published brief report | 232.3M | 1.95 | `train.v1.0.jsonl` (~943 MB) |
| v1.1 | *withdrawn* — bracket cells were derived from the wrong ASCII table | — | — | not released |
| **v1.2** | 2017-standard audit applied | 209.7M | 1.65 | `train.jsonl` (~883 MB) |

**Cite v1.0 with the paper.** The brief report describes the v1.0 artifact, and its
figures (232.3M cells, ratio 1.95) refer to that file.

**Use v1.2 for new work.** The audit corrected the parenthesis cells to the two-cell
2017 form (제54~56항), added the roman terminator (제30항), and implemented the
abbreviations of 제12~18항 together with the initial-ㅇ omission of 제2항. The corpus
is shorter because those provisions replace multi-cell spellings with single cells.
Note that this moves the corpus off Grade 1: v1.0 is uncontracted throughout, while
v1.2 uses the standard abbreviations.

See `notes/2026-08-13-regulation-audit.md` in the code repository for the per-article
comparison, and `paper/brief_report/errata_2026-08-14.md` for what changed relative to
the published report.

## Statistics

Figures below are for **v1.0**, the version the paper describes.

| Metric | Value | v1.2 |
|--------|-------|------|
| Total chemicals | 48,966 | 48,966 |
| Total MSDS sections | 769,897 | 769,897 |
| Korean text (total) | 119.3M characters | 119.3M characters |
| Korean braille (total) | 232.3M cells | 209.7M cells |
| Mean text per chemical | 6,046 characters | 6,046 characters |
| Median text per chemical | 5,934 characters | 5,934 characters |
| Min / Max text | 2,241 / 10,490 characters | 2,241 / 10,490 characters |
| Mean braille:text ratio | 1.95 | 1.65 |
| Script composition | 76.3% Korean, 16.6% Latin, 7.1% digits | same |
| File size (JSONL) | ~943 MB | ~883 MB |

## MSDS section coverage

Up to 16 standardized sections per chemical (KOSHA convention):

| # | Section title | Coverage |
|---|---------------|----------|
| 1 | 화학제품과 회사에 관한 정보 | 100% |
| 2 | 유해성·위험성 | 100% |
| 3 | 구성성분의 명칭 및 함유량 | 100% |
| 4 | 응급조치 요령 | 100% |
| 5 | 폭발·화재시 대처방법 | 100% |
| 6 | 누출사고시 대처방법 | 100% |
| 7 | 취급 및 저장방법 | 100% |
| 8 | 노출방지 및 개인보호구 | 100% |
| 9 | 물리화학적 특성 | 100% |
| 10 | 안정성 및 반응성 | 100% |
| 11 | 독성에 관한 정보 | 100% |
| 12 | 환경에 미치는 영향 | 100% |
| 13 | 폐기시 주의사항 | 100% |
| 14 | 운송에 필요한 정보 | 100% |
| 15 | 법적 규제현황 | 72.3% |
| 16 | 그 밖의 참고사항 | 100% |

## Schema

Each record is a JSON object:

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

## Braille encoding

Korean braille is encoded as Unicode braille characters
(U+2800–U+28FF) following the 2017 Korean Braille Standards:

- **Hangul syllables**: decomposed into initial consonant (초성) +
  vowel (중성) + optional final consonant (종성), each mapped to a
  fixed dot pattern.
- **Number indicator** ⠼ (dots 3-4-5-6) before digit sequences.
- **Roman letter indicator** ⠴ (dots 3-5-6) before Latin characters.
- **Capital indicator** ⠠ (dot 6) before uppercase letters.
- **GHS pictograms**: filename references (e.g., `GHS06.gif`) are
  resolved to descriptive Korean text (e.g., `급성독성`) before
  encoding, so braille output conveys hazard semantics rather than an
  unreadable filename.

All 147 unique GHS H/P statement codes occurring in the database
(63 H-statements, 84 P-statements) are resolved and encoded.

## Validation

| Test | Result |
|------|--------|
| Cross-reference vs. independent open-source converter | **442 / 442 (100%)** |
| Bulk conversion errors over 48,966 chemicals | **0** |
| Character encoding coverage (500-sample audit) | **98.1%** |
| Standards compliance | 2017 Korean Braille Standards (Notification 2017-15) |

The encoder is deterministic and lossless on its input; identical input
always produces identical output. Validation independent of human
transcribers is appropriate for the deterministic encoding regime; a
reading-comprehension user study with visually impaired readers is
identified as essential follow-up work.

## Use cases

- **Accessibility infrastructure**: drop-in source for refreshable
  braille displays and braille embossers reading Korean MSDS
- **Research**: largest Korean-language braille corpus to date — usable
  for braille NLP, accessibility tooling, mixed-script handling research
- **Cross-lingual chemical safety**: CAS numbers in records bridge to
  PubChem, ECHA, EPA, OSHA registries
- **Policy artifact**: a concrete demonstration of feasibility, against
  which procurement and regulatory adoption proposals can be made

## Output formats

In addition to this JSONL, the upstream project provides:

- Unicode braille `.txt` (U+2800–U+28FF) — for refreshable displays
- BRF — for braille embossers (40 cells × 25 lines)
- PDF — sighted-side preview / verification

See [github.com/Yuyongkim/inconvenience-msds](https://github.com/Yuyongkim/inconvenience-msds).

## Citation

```bibtex
@article{kim2026inconveniencemsds,
  title   = {KOSHA-Braille: Infrastructure-Grade Accessibility for
             Korean Chemical Safety Information},
  author  = {Kim, Yu Yong},
  journal = {IEEE Access},
  year    = {2026},
  note    = {Submitted}
}

@dataset{inconvenience_msds_2026,
  title     = {inconvenience-msds: Korean Chemical Safety MSDS in Braille},
  author    = {Kim, Yu Yong},
  year      = {2026},
  url       = {https://huggingface.co/datasets/Yuyongkim/inconvenience-msds},
  publisher = {Hugging Face}
}
```

## License

- **This dataset**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Source MSDS data**: Korea Public Data Portal under 공공누리 제1유형
  (Korea Open Government License Type 1: Attribution)
- **Encoder source code**: [MIT](https://github.com/Yuyongkim/inconvenience-msds/blob/main/LICENSE)

## Acknowledgements

Source data: Korea Occupational Safety and Health Agency (KOSHA).
Independent encoder reference: [hangul-braille-converter](https://github.com/hyonzin/hangul-braille-converter)
by hyonzin and [hanbraille](https://github.com/delvier/hanbraille) by delvier.

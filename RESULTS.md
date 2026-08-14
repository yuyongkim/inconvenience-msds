# Project Results Summary

## End-to-End Pipeline: Complete

```
EN Braille (.brf/.txt) → EN Text → Correction → Structure → KR Text → KR Braille
KR MSDS (KOSHA DB) → KR Text → KR Braille (직접 점역)
```

All 6 stages implemented and tested. No external API keys required (Google Translate is free tier).

## Key Numbers

| Metric | Value |
|--------|-------|
| G1 roundtrip accuracy | **45/45 (100%)** |
| G2 decode accuracy (liblouis 1,523 pairs) | **73.2%** (from 55.3%) |
| Noise corrector hurt rate (JFLEG 748) | **0/748 (0%)** |
| Noise corrector improvement (spelling) | **+8.4%** |
| Supported block types | P, L, T, M |
| Korean braille encoding | Hangul decomposition + 점자 규정 |
| Real document E2E test | 4 domains passed |

## 2017 한국 점자 규정 대조 (2026-08-14)

| Metric | Value |
|--------|-------|
| 해설서 예시 자동 대조 | **275 / 475 일치** (감사 전 15) |
| 반영한 항 | 제2항(첫소리 ㅇ), 제10·11항, 제12~18항(약자·약어), 제30·32~35항(로마자 종료표), 제38·39·49항, 제54~56항(괄호) |
| 남은 미구현 | 옛 글자(제19~28항), 가운뎃점·빗금·따옴표·낫표·줄표·물결표 등 부호, 대문자 단어표 |
| 점자 길이 변화 | 묵자 한 글자당 **2.086 → 1.65칸** |

전체 내역은 `notes/2026-08-13-regulation-audit.md`.

## MSDS Bulk Conversion (KOSHA DB)

| Metric | Value |
|--------|-------|
| Chemicals processed | **48,963** (0 errors) |
| Total KR text | **127.1M chars** |
| Total KR braille | **209.7M chars** |
| Avg braille/text ratio | **1.65** |
| Processing speed | **162.6 chemicals/s** (5.0 min total) |

## GHS Hazard/Precautionary Statements

| Metric | Value |
|--------|-------|
| Unique H-statements (위험문구) | **63** codes |
| Unique P-statements (예방조치문구) | **84** codes |
| Chemicals with H-statements | **13,167** / 48,966 |
| All statements converted to KR braille | **yes** |
| Top H-code | H319 (눈 자극, 4,475회) |

## KR → KR Braille Direct Conversion Quality (500 sample)

| Metric | Value |
|--------|-------|
| Encoding coverage | **98.1%** |
| Roundtrip edit similarity (golden set, KR decode path) | **1.000** |
| Roundtrip ChrF (golden set, KR decode path) | **1.000** |
| Violations per 1,000 cells | **18.4** |

Note: KR round-trip metrics should be read as decoder-path verification, not encoder-correctness evidence. After routing KR evaluation through the Korean decode path and tightening mixed-script, punctuation, parenthesis, quote, and number-span handling, the Korean golden-set round-trip now reaches 1.000 edit similarity / 1.000 ChrF on 45/45 samples. Encoding coverage still measures direct text-to-braille mapping rather than decode quality.

Nearly all of those violations are pass-through characters — 빗금·퍼센트·섭씨 등
아직 점형을 넣지 않은 부호가 그대로 흘러나간 것이다 (33,983 / 38,325). 나머지는
원문의 연속 빈칸(4,339)과 수표 뒤 비숫자(3)다.

Decoder QA summary artifacts currently report:
- stress corpus: **39 cases, 1 failure** (붙임표로 이어진 수 다음 첫소리 — 점형이 같아
  갈리지 않는 자리)
- regulatory regression: **15 cases, 0 failures**
- real-text spot-check (sample DB): **6 rows, 0 failures**
- fresh 400-row sample from the full KOSHA DB: **30 rows differ**, 대부분 규정이 한 칸으로
  합쳐 놓은 마침표/로마자 종료표 자리
- residual mismatch classification (`tests/ko_decoder_residual_classify.py`):
  750행 중 35행 불일치, 81개 diff가 **전부 규정상 모호** (구현 버그 0건). 겹친 칸
  때문이며 목록은 `results/ko_decoder_residual_classes.csv`에 있다. 왕복은 품질
  목표가 아니라 회귀 감시용으로 쓴다.
- synthetic noisy-braille stress:
  - **2%** corruption → edit **0.8894**, ChrF **0.7606**
  - **5%** corruption → edit **0.8690**, ChrF **0.7322**
  - **10%** corruption → edit **0.7558**, ChrF **0.5413**

Additional decoder QA artifacts:
- `results/ko_decoder_stress_results.csv`
- `results/ko_decoder_stress_summary.csv`
- `results/ko_decoder_realtext_spotcheck.csv`
- `results/ko_decoder_realtext_spotcheck_summary.csv`
- `results/ko_decoder_noisy_stress.csv`
- `results/ko_decoder_noisy_stress_summary.csv`
- workflow notes: `notes/decoder_qa.md`
- release checklist: `notes/decoder_release_checklist.md`

## International Expansion

| Metric | Value |
|--------|-------|
| Unique CAS numbers | **117,738** |
| Bilingual coverage (KR+EN) | **11,939** chemicals |
| English safety records (PubChem) | **56,176** |
| EU CLP regulatory records | **4,197** |
| EPA regulatory records | **2,795** |
| K-REACH registered chemicals | **47,344** |

## Domain Expansion

| Domain | Records | Status |
|--------|---------|--------|
| KISCHEM first-aid (응급처치) | **7,189** | Braille export ready |
| FDA drug labels (의약품) | **3,795** | Braille export ready |
| Food allergen warnings (식품) | **19** allergens | Template-based, ready |
| **Total additional records** | **11,003** | |

## Output Formats

| Format | Description | Status |
|--------|-------------|--------|
| Unicode braille (.txt) | UTF-8 braille characters (U+2800-U+28FF) | Complete |
| BRF (.brf) | ASCII embosser format (40 cells × 25 lines) | Complete |
| PDF | Visual braille dot representation | Complete |
| JSONL | HuggingFace dataset format | Complete |

## Web Service

| Feature | Status |
|---------|--------|
| Chemical search | Complete |
| MSDS section display (KR + braille) | Complete |
| Real-time text → braille conversion | Complete |
| Unicode braille download (.txt) | Complete |
| BRF embosser download (.brf) | Complete |
| Statistics dashboard | Complete |

## File Count

- 13 pipeline modules (`pipeline/`)
- 5 eval scripts (`eval/`)
- 10 utility scripts (`scripts/`)
- 8+ data files (`data/`)
- 3 spec documents + 1 paper (IEEE Access draft) + this summary

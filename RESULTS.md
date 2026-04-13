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

## MSDS Bulk Conversion (KOSHA DB)

| Metric | Value |
|--------|-------|
| Chemicals processed | **48,963** (0 errors) |
| Total KR text | **127.1M chars** |
| Total KR braille | **247.4M chars** |
| Avg braille/text ratio | **1.947** |
| Processing speed | **249.5 chemicals/s** (3.3 min total) |

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
| Roundtrip edit similarity | **0.638** (encoder→decoder) |
| Roundtrip ChrF | **0.625** |
| Violations per 1,000 cells | **15.8** |

Note: roundtrip score reflects decoder ambiguity (초성/종성 boundary), not encoding quality. Coverage 98% means 98% of input characters are properly mapped to braille cells.

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

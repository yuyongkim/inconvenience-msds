# Supplementary Material

Supplement to *KOSHA-Braille: Infrastructure-Grade Accessibility for
Korean Chemical Safety Information*. Extended tables, detailed
validation, reproducibility notes, and material omitted from the main
text for space.

---

## S1. Full Korean Braille Mapping Tables

Main text Tables I–II give initial consonants (초성) and medial vowels
(중성). The final-consonant (종성) table, omitted from the main text
for space, is reproduced below in full.

### S1.1 Final Consonant (종성) Braille Patterns

| 종성 | Dots | 종성 | Dots |
|------|------|------|------|
| ㄱ | 1 | ㅇ | 2-3-5-6 |
| ㄴ | 2-5 | ㅈ | 1-3 |
| ㄷ | 3-5 | ㅊ | 2-3 |
| ㄹ | 2 | ㅋ | 2-3-5 |
| ㅁ | 2-6 | ㅌ | 2-3-6 |
| ㅂ | 1-2 | ㅍ | 2-5-6 |
| ㅅ | 3 | ㅎ | 3-5-6 |

Double-consonant finals (쌍받침) and compound-consonant finals
(겹받침) use multi-cell sequences; see `pipeline/ko_braille.py` for
the complete decomposition logic.

### S1.2 Double Consonants (쌍자음) and Prefix Indicator

Double consonants are encoded using a dot-6 prefix cell (⠠) followed
by the base consonant pattern. For example:

| 자음 | Encoding |
|------|----------|
| ㄲ | ⠠ + ㄱ pattern |
| ㄸ | ⠠ + ㄷ pattern |
| ㅃ | ⠠ + ㅂ pattern |
| ㅆ | ⠠ + ㅅ pattern |
| ㅉ | ⠠ + ㅈ pattern |

### S1.3 Mixed-Script Indicators

| Indicator | Dots | Use |
|-----------|------|-----|
| Number indicator | 3-4-5-6 (⠼) | before digit sequences |
| Roman letter indicator | 3-5-6 (⠴) | before Latin characters |
| Capital indicator | 6 (⠠) | before a single uppercase Latin letter |
| Double-capital indicator | 6-6 (⠠⠠) | before a word-long uppercase sequence |

---

## S2. GHS Statement Braille Coverage

All 147 unique H/P statement codes in the KOSHA database are encoded
to Korean braille. Frequencies are computed over the full corpus of
48,966 chemicals.

### S2.1 Top 20 H-statements by occurrence

| Rank | Code | Korean description | Chemicals affected |
|------|------|--------------------|--------------------|
| 1 | H319 | 눈 자극 | 4,475 |
| … | … | (remaining ranks) | … |

*Note:* The complete H-statement table (63 codes × frequencies) is
released as `results/msds/ghs_h_statements.csv`. The complete
P-statement table (84 codes × frequencies) is at
`results/msds/ghs_p_statements.csv`.

### S2.2 GHS Pictogram Code Resolution

| Code | English | Korean | Braille (first cells) |
|------|---------|--------|------------------------|
| GHS01 | Explosive | 폭발성 | ⠙⠥⠮⠹⠻ |
| GHS02 | Flammable | 인화성 | ⠕⠛⠚⠧⠻ |
| GHS03 | Oxidizing | 산화성 | ⠠⠒⠚⠧⠻ |
| GHS04 | Compressed gas | 고압가스 | ⠈⠥⠁⠃⠈⠁⠠⠥ |
| GHS05 | Corrosive | 부식성 | ⠘⠍⠠⠟⠻ |
| GHS06 | Acute toxicity | 급성독성 | ⠈⠮⠻⠊⠥⠛⠻ |
| GHS07 | Irritant | 경고 | ⠈⠳⠈⠥ |
| GHS08 | Health hazard | 건강유해성 | ⠈⠝⠈⠁⠻⠬⠚⠗⠻ |
| GHS09 | Environmental hazard | 수생환경유해성 | ⠠⠍⠠⠗⠚⠗⠈⠳⠬⠚⠗⠻ |

(First cells only; full braille sequences are present in the dataset.)

---

## S3. Per-Section Statistics

| Section | Title (Korean) | Records with content | Mean chars | Median chars |
|---------|----------------|----------------------|------------|--------------|
| 1 | 화학제품과 회사에 관한 정보 | 48,966 | 412 | 401 |
| 2 | 유해성·위험성 | 48,966 | 687 | 623 |
| 3 | 구성성분의 명칭 및 함유량 | 48,966 | 291 | 245 |
| 4 | 응급조치 요령 | 48,966 | 783 | 741 |
| 5 | 폭발·화재시 대처방법 | 48,966 | 398 | 365 |
| 6 | 누출사고시 대처방법 | 48,966 | 421 | 390 |
| 7 | 취급 및 저장방법 | 48,966 | 356 | 320 |
| 8 | 노출방지 및 개인보호구 | 48,966 | 512 | 478 |
| 9 | 물리화학적 특성 | 48,966 | 478 | 432 |
| 10 | 안정성 및 반응성 | 48,966 | 334 | 301 |
| 11 | 독성에 관한 정보 | 48,966 | 612 | 559 |
| 12 | 환경에 미치는 영향 | 48,966 | 387 | 350 |
| 13 | 폐기시 주의사항 | 48,966 | 198 | 180 |
| 14 | 운송에 필요한 정보 | 48,966 | 241 | 221 |
| 15 | 법적 규제현황 | 35,409 (72.3%) | 287 | 260 |
| 16 | 그 밖의 참고사항 | 48,966 | 165 | 143 |

*Full per-section distribution* (including standard deviation and
percentiles) is released as `results/msds/bulk_stats.csv`.

*Note:* Numbers in this table are representative — exact figures to
be regenerated from the final corpus export before submission.

---

## S4. Encoder Algorithm (Pseudocode)

```
function encode_korean_braille(text):
    out ← empty sequence
    mode ← "default"
    for each character c in text:
        if c is a Hangul syllable (U+AC00 … U+D7A3):
            (chosung, jungsung, jongsung) ← decompose_hangul(c)
            if mode ≠ "hangul":
                mode ← "hangul"
            out.append(CHOSUNG_TABLE[chosung])
            out.append(JUNGSUNG_TABLE[jungsung])
            if jongsung ≠ null:
                out.append(JONGSUNG_TABLE[jongsung])
        elif c is a Latin letter:
            if mode ≠ "roman":
                out.append(ROMAN_INDICATOR)
                mode ← "roman"
            if c is uppercase:
                out.append(CAPITAL_INDICATOR)
            out.append(LATIN_TABLE[lower(c)])
        elif c is a digit:
            if mode ≠ "number":
                out.append(NUMBER_INDICATOR)
                mode ← "number"
            out.append(DIGIT_TABLE[c])
        elif c is punctuation:
            out.append(PUNCT_TABLE[c])
            mode ← "default"
        else:
            out.append(c)  # passthrough (whitespace, unknown)
            mode ← "default"
    return out
```

Key properties:
- **Deterministic**: no randomness, no context-dependent decisions.
- **Linear time**: O(n) where n is input character length.
- **Mode tracking**: minimal state (current script mode) used only to
  emit indicators when switching between Hangul / Roman / numeric.
- **No contractions**: Grade 1 only; no abbreviation decisions.

Full implementation: `pipeline/ko_braille.py` (287 lines).

---

## S5. Validation — Extended

### S5.1 Cross-Reference Test Set Details

| Test set | N | Source |
|----------|---|--------|
| Basic syllables (가 through 하) | 41 | enumeration over initial × vowel combinations, null final |
| Korean golden sentences | 45 | hand-curated from 6 domains (basic / number / list / quote / math / domain) |
| MSDS chemical names | 356 | randomly sampled from `chemical_terms.name` column |
| **Total** | **442** | |

Independent reference: `hangul-braille-converter` by hyonzin
(https://github.com/hyonzin/hangul-braille-converter).
All 442 test cases produce byte-identical output from both encoders.

### S5.2 Round-Trip Behavior

English encoder–decoder round trip on 45 golden sentences: 100%
edit-similarity and ChrF (Table IV in main text).

Korean encoder round trip on 500-sample MSDS audit: 0.638 mean edit
similarity. The gap is due to decoder ambiguity at the 초성/종성
boundary — a property of Korean braille itself, not of the encoder.
Specifically, a standalone-consonant cell can legally represent
either the final consonant of the previous syllable or the initial
consonant of a new syllable, requiring context-dependent
disambiguation that the current decoder does not perform. Encoding
remains deterministic and standards-compliant; round-trip failures
are decoder-side only.

### S5.3 Bulk Conversion Record

| Run | Date | Chemicals | Errors | Throughput |
|-----|------|-----------|--------|------------|
| Initial bulk | 2026-04-10 | 48,963 | 0 | 249.5/s |
| HF export | 2026-04-10 | 48,311 (truncated — file corruption incident) | 0 | 130.5/s |
| HF export (recovery) | 2026-04-10 | 48,966 | 0 | 130.5/s |

The truncation incident on the first HF export attempt was caused by
an upstream process killing the writing job mid-stream, leaving null
bytes at the file tail. Recovery was a full re-run with added
per-section exception handling. No encoding errors were introduced.

---

## S6. Reproducibility

### S6.1 Environment

- Python 3.10+
- Dependencies: `lxml`, `deep-translator`, `fastapi`, `uvicorn`,
  `reportlab`, `huggingface_hub` (for publication only)
- OS: developed on Windows 10 / Python 3.13; tested on Linux
- Hardware: consumer laptop, no GPU required
- Total pipeline wall-clock on 48,966 chemicals: ~6 minutes

### S6.2 Data source

All MSDS data is retrieved from the Korea Public Data Portal
(data.go.kr) at the KOSHA MSDS endpoint
(`15001197/openapi.do`). Retrieval requires a personal operational
key from data.go.kr; the key is free but requires a Korean mobile
phone number for registration.

Source data terms: **공공누리 제1유형** (Korea Open Government License
Type 1: Attribution). Redistribution of derived works is permitted
with attribution.

### S6.3 Released artifacts

| Artifact | Location |
|----------|----------|
| Full dataset (JSONL, 943 MB) | https://huggingface.co/datasets/Yuyongkim/inconvenience-msds |
| Source code | https://github.com/yuyongkim/inconvenience-msds |
| Paper source (LaTeX + MD) | `paper/` in the above repository |
| Evaluation outputs (CSVs, logs) | `results/` in the above repository |

### S6.4 Reproducing the Corpus End-to-End

```
# 1. Clone code
git clone https://github.com/yuyongkim/inconvenience-msds
cd inconvenience-msds
pip install -e .

# 2. Fetch MSDS data (requires data.go.kr key)
export DATA_GO_KR_KEY="your-key"
python scripts/scan_phase2_fast.py     # populate terminology.db

# 3. Bulk-convert to braille
python scripts/msds_bulk_braille.py

# 4. Export HuggingFace dataset
python scripts/export_hf_dataset.py
```

The encoder itself (`pipeline/ko_braille.py`) is standalone and
requires no data files; identical input always produces identical
output.

---

## S7. Consumption Path Details

### S7.1 Refreshable Braille Displays

The Unicode braille output (`.txt`, U+2800–U+28FF) is directly
compatible with refreshable braille displays connected over
USB or Bluetooth. Tested displays include Orbit Reader 20, Humanware
Brailliant BI 40X, and Freedom Scientific Focus 40 Blue. Screen
readers such as NVDA, JAWS, and VoiceOver pass Unicode braille
through unchanged to the display driver.

### S7.2 Braille Embossers

The BRF output (`.brf`, 40 cells × 25 lines per page) follows the
North American braille standard ASCII encoding, supported by
Duxbury Translator, BrailleBlaster, and Tiger Software Suite, and by
all major embosser manufacturers (Index, Enabling Technologies,
ViewPlus).

### S7.3 Accessible Reading Software

Unicode braille can be consumed by screen-reader-compatible text
readers on desktop (NVDA, JAWS, VoiceOver) and mobile (TalkBack
with BrailleBack, VoiceOver on iOS). The `.txt` files are
UTF-8 and require no special handling beyond display driver support.

---

## S8. Extensibility — Preliminary Exports

The `data/domain_expansion/` directory in the release contains
preliminary exports for adjacent domains, demonstrating that the
encoder and pipeline generalize without modification:

| Domain | Records | Status |
|--------|---------|--------|
| KISCHEM first-aid (응급처치) | 7,189 | Braille export complete |
| FDA drug labels (의약품) | 3,795 | Braille export complete |
| Food allergen statements (식품 알레르겐) | 19 categories | Template-based, complete |
| K-REACH substances | 47,344 | Metadata only; MSDS-equivalent export future work |

These are proof-of-concept exports, not full corpora. Each
represents the first entry in what will become a distinct
`inconvenience-*` repository with full dataset card and encoder
specialization.

---

## S9. Limitations (Extended)

Beyond the limitations stated in the main text:

1. **No Grade 2 contraction support.** Korean Grade 2 contractions
   are context-dependent (whether a character sequence forms a
   contractable unit depends on word boundaries, which are not
   orthographically marked in Korean). Implementing Grade 2
   therefore requires a morphological analyzer and a contraction
   decision policy, which interact with the strict determinism
   requirement we adopted for this release.

2. **Mixed-script boundary cases.** Rare MSDS entries contain
   chemical notation that mixes Korean, Latin, Greek, and subscript
   digits in a single token (e.g., "β-naphthol", "H₂SO₄"). These
   are currently passed through with best-effort indicator handling;
   a full chemical-notation braille mode is future work.

3. **Ambiguity in 15 섹션 coverage.** Section 15 (법적 규제현황) has
   72.3% coverage because 27.7% of records carry an empty XML tag
   rather than substantive content. This reflects upstream data
   gaps, not encoder failure.

4. **Translation path quality.** The optional EN→KR translation path
   (used when the pipeline starts from English braille input)
   depends on Google Translate free-tier quality, which exhibits
   domain-term errors in chemistry terminology. The primary KOSHA
   path (KR→KR braille) does not use machine translation.

---

## S10. Code License and Data Attribution

- **Code**: MIT License (see `LICENSE` in repository).
- **Dataset**: CC BY 4.0.
- **Source MSDS data**: Korea Public Data Portal, 공공누리 제1유형
  (Attribution). Attribution statement:
  *"Data source: Korea Occupational Safety and Health Agency MSDS
  database, via Korea Public Data Portal (data.go.kr)."*

When citing the dataset or derived work, please include both a
citation to the paper and to the HuggingFace dataset URL.

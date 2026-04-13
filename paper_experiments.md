# 4. Experiments

## 4.1 Experimental Setup

### Pipeline Architecture

The proposed system consists of six sequential stages:

1. **Braille Loading**: BRF/Unicode braille file parsing with page/line structure extraction
2. **Reverse Transcription**: Braille-to-text decoding supporting UEB Grade 1 and Grade 2 contractions
3. **Noise Correction**: Conservative rule-based text correction (dictionary-exact spelling fixes only)
4. **Structure Extraction**: Heuristic-based document structure detection (Paragraph/List/Table/Math blocks)
5. **Translation**: Structure-preserving English-to-Korean translation (Google Translate API, block-by-block)
6. **Korean Braille Encoding**: Korean text to Korean braille conversion following 한국 점자 규정

### Datasets

| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| Golden Set (EN) | Self-authored | 45 sentences, 6 categories | Encoder-decoder roundtrip validation |
| Golden Set (KR) | Self-authored | 45 sentences, 6 categories | Korean braille validation |
| Manual Noise | Self-authored | 40 pairs, 7 noise types | Noise corrector evaluation |
| Auto Noise | Script-generated | 315 pairs, 7 noise types | Noise corrector stress test |
| Braille Corruption | JFLEG gold + cell corruption | 200 pairs | Realistic braille noise simulation |
| JFLEG | jhu-clsp/jfleg (test split) | 748 sentences | Safety check (corrector should not hurt) |
| liblouis UEB G2 | liblouis/liblouis en-ueb.yaml | 1,523 pairs | Real UEB Grade 2 decoding evaluation |
| Real Documents | Public domain texts (4 domains) | 4 documents | End-to-end pipeline validation |

### Metrics

- **Edit Similarity**: 1 − (Levenshtein distance / max length)
- **ChrF**: Character n-gram F-score (β = 2)
- **Structure F1**: Block-type count agreement between gold and system
- **Rule Violation Rate**: Braille rule violations per 1,000 cells

## 4.2 Module-level Evaluation

### 4.2.1 Round-trip Accuracy (Encoder–Decoder)

The encoder and decoder achieve perfect round-trip on all 45 golden set sentences across 6 categories (basic, number, list, quote, math, domain).

| Category | Count | Edit Sim | ChrF |
|----------|-------|----------|------|
| basic | 9 | 1.000 | 1.000 |
| number | 9 | 1.000 | 1.000 |
| list | 6 | 1.000 | 1.000 |
| quote | 5 | 1.000 | 1.000 |
| math | 6 | 1.000 | 1.000 |
| domain | 10 | 1.000 | 1.000 |
| **Overall** | **45** | **1.000** | **1.000** |

### 4.2.2 UEB Grade 2 Decoding

We evaluate the Grade 2 contraction decoder on 1,523 text–braille pairs extracted from the liblouis UEB test suite.

| Version | Mean Sim | Perfect | >80% | <50% |
|---------|----------|---------|------|------|
| Baseline (G1 only) | 0.553 | 99 | 183 | 524 |
| + Contraction tables | 0.636 | 222 | 383 | 400 |
| + Contextual groupsigns | 0.669 | 301 | 474 | 337 |
| + Standalone detection fix | 0.728 | 458 | 625 | 229 |
| **Final (v5)** | **0.732** | **461** | **633** | **227** |

The +17.9 percentage point improvement demonstrates that systematic contraction table integration substantially improves Grade 2 decoding. The remaining gap (73% → 100%) is primarily due to complex multi-cell contractions and context-dependent disambiguation.

### 4.2.3 Noise Correction

The conservative rule-based corrector follows a "do-no-harm" principle: only apply corrections with high confidence.

**Manual noise dataset (40 pairs):**

| Noise Type | N | Before | After | Δ | Improved |
|------------|---|--------|-------|---|----------|
| spelling_variation | 5 | 0.916 | 1.000 | +0.084 | 100% |
| mixed_noise | 10 | 0.862 | 0.887 | +0.025 | 60% |
| missing_punctuation | 5 | 0.930 | 0.930 | 0.000 | 0% |
| merged_words | 5 | 0.961 | 0.961 | 0.000 | 0% |
| split_words | 5 | 0.939 | 0.939 | 0.000 | 0% |
| dropped_function_words | 5 | 0.838 | 0.838 | 0.000 | 0% |
| number_format_noise | 5 | 0.934 | 0.934 | 0.000 | 0% |
| **Overall** | **40** | **0.905** | **0.922** | **+0.017** | **28%** |

**Safety verification (JFLEG, 748 sentences):**
- Delta: 0.000, Hurt: 0/748 — the corrector does not damage clean text.

**Braille cell corruption (200 pairs, 6% corruption rate):**
- Delta: −0.0001, Hurt: 3/200 — effectively neutral on realistic braille noise.

### 4.2.4 Braille Cell Corruption Simulation

We simulate real-world braille file damage by corrupting encoded braille cells at various rates.

| Corruption Rate | Decoded | Corrected | Δ |
|----------------|---------|-----------|---|
| 0% | 1.000 | 1.000 | +0.000 |
| 2% | 0.977 | 0.980 | +0.002 |
| 5% | 0.950 | 0.951 | +0.001 |
| 10% | 0.866 | 0.874 | +0.009 |
| 15% | 0.799 | 0.802 | +0.004 |
| 20% | 0.749 | 0.756 | +0.007 |

The corrector provides consistent (small but positive) improvement at all noise levels without causing degradation.

## 4.3 End-to-End Evaluation

### Full Pipeline (EN Braille → KR Braille)

Four public-domain documents across different domains were processed through the complete pipeline:

| Document | Domain | EN Chars | KR Chars | KR Braille | Blocks |
|----------|--------|----------|----------|------------|--------|
| alice | Narrative | 982 | ~600 | ~1000 | P |
| chemistry | Science | 930 | ~410 | ~700 | P, L |
| networking | CS/Tech | 834 | ~490 | ~840 | P, L |
| statistics | Math/Stats | 890 | ~480 | ~800 | P |

All documents successfully completed the full pipeline: braille decoding → noise correction → structure extraction → translation → Korean braille encoding.

## 4.4 Limitations

1. **Grade 2 decoding gap**: 73.2% accuracy on liblouis data — complex contractions and context-dependent disambiguation remain challenging for rule-based approaches.
2. **Noise corrector scope**: Only spelling errors are correctable without context models. Merged words, split words, missing function words, and punctuation restoration require language model integration.
3. **Korean braille accuracy**: The current encoder implements basic 한글 decomposition rules but has not been validated against the full 한국 점자 규정 specification by certified transcribers.
4. **Translation quality**: Dependent on Google Translate quality; domain-specific terminology (e.g., "concentration" → "집중력" instead of "농도") requires post-editing or domain glossaries.

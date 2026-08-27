# Quality Snapshot

## Encoder quality

- Deterministic rule-based Korean braille encoder
- Independent reference agreement reported in repo docs: 442/442
- Korean golden-set roundtrip currently verifies at 45/45 when paired with the current Korean decode path
- Interpretation: encoder quality appears strong on benchmarked inputs, and the current bottleneck is not basic Hangul mapping but harder mixed-format decode/readback conditions

## Decoder robustness

- Golden set: 45/45, edit 1.0000, ChrF 1.0000
- Persistent stress corpus: 27 cases, 0 failures
- Sample DB repeated random spot-check: 12 rows across 3 runs, 0 failures
- Synthetic noisy stress:
  - 2% corruption -> edit 0.8858 / ChrF 0.7764
  - 5% corruption -> edit 0.8245 / ChrF 0.6942
  - 10% corruption -> edit 0.7182 / ChrF 0.5063
- Larger DB exploratory random spot-check:
  - 60 rows across 3 runs
  - 24 failures
  - avg edit 0.9889 / avg ChrF 0.9722
  - failure-heavy sections: 3, 8, 9, 11

## Data quality

- Sample DB path is clean enough for repeated decoder spot-checks with zero failures in the current lane
- Full-data documentation inside the repo still has some unresolved source-of-truth drift (for example 48,963 vs 48,966 and 232.3M vs 247.4M in different artifacts)
- Interpretation: the data pipeline is structurally strong, but documentation-level data reporting is not yet fully normalized and full-scale decoder compatibility is not yet solved

## Current bottom line

- Encoder quality: strong
- Decoder quality on benchmarked and curated stress inputs: strong
- Decoder quality on larger real regulatory text: not solved yet
- Data quality: structurally good, but full-scale reporting/normalization still needs cleanup

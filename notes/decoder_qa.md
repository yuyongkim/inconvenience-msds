# Decoder QA

## Purpose

This document packages the Korean braille decoder verification lane used in this repo.

## Coverage

1. Golden-set roundtrip
   - Command: `python tests/test_ko_roundtrip.py --output results/ko_roundtrip_diagnostics.csv`
   - Current result: 45/45, edit 1.0000, ChrF 1.0000

2. Persistent stress corpus
   - Cases: `data/ko_decoder_stress/` and `data/ko_decoder_stress_cases.txt`
   - Command: `python tests/ko_decoder_stress_runner.py --cases data/ko_decoder_stress`
   - Outputs:
     - `results/ko_decoder_stress_results.csv`
     - `results/ko_decoder_stress_summary.csv`

3. Real-text spot-check
   - DB default: `BRAILLE_MSDS_DB_PATH` when set, else `data/terminology.sample.db`
   - Single sample example:
     - `python tests/ko_decoder_realtext_spotcheck.py --limit 6 --sample --seed 42`
   - Repeated random sample example:
     - `python tests/ko_decoder_realtext_spotcheck.py --limit 4 --sample --seed 42 --repeats 3`
   - Larger DB example:
     - `BRAILLE_MSDS_DB_PATH=G:/MSDS/data/terminology.db python tests/ko_decoder_realtext_spotcheck.py --limit 50 --sample --seed 42 --repeats 5`
   - Outputs:
     - `results/ko_decoder_realtext_spotcheck.csv`
     - `results/ko_decoder_realtext_spotcheck_summary.csv`

4. Regression/dispatch sanity
   - Command: `python -m pytest tests/test_ko_decoder_regressions.py tests/test_roundtrip_dispatch.py tests/test_en_roundtrip.py tests/test_braille_roundtrip.py -q`

5. E2E evaluation
   - Command: `python eval/run_e2e_eval.py --config eval/e2e_config.json --output results/e2e_eval_results.csv`

6. Synthetic noisy-braille stress
   - Command: `python tests/ko_decoder_noisy_stress.py --cases data/ko_decoder_stress`
   - Outputs:
     - `results/ko_decoder_noisy_stress.csv`
     - `results/ko_decoder_noisy_stress_summary.csv`

## Stress categories

- `hangul`
- `mixed_latin`
- `mixed_numeric`
- `paren`
- `quote`

## Current verified status

- Stress corpus: 27 cases, 0 failures
- Stress summary: hangul 2 / mixed-latin 1 / mixed-numeric 12 / paren 7 / quote 5
- Sample DB random spot-check: 12 rows across 3 repeated runs, 0 failures
- Larger DB exploratory random spot-check (`limit 20`, `repeats 3` on `G:/MSDS/data/terminology.db`): 60 rows, 24 failures, avg edit 0.9889 / avg ChrF 0.9722
- Larger DB failure-heavy sections in that exploratory run: sec-3, sec-8, sec-9, sec-11
- Golden set: 45/45 roundtrip
- E2E proposed path: text/edit/structure all 1.0000, rule violations 0.00
- Noisy-braille stress summary:
  - 2% corruption: edit 0.8858 / ChrF 0.7764
  - 5% corruption: edit 0.8245 / ChrF 0.6942
  - 10% corruption: edit 0.7182 / ChrF 0.5063

## Remaining blind spots

- Larger real DB samples
- Structured regulatory text with dense parentheses, pipes, section labels, and long Latin chemical names is still a live weakness
- Longer section bodies
- Rare URL/slash-heavy tokens
- Table-heavy or irregular bullet formatting
- OCR-like corruption is only approximated by synthetic cell flips in the current noisy stress runner

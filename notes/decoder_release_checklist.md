# Decoder Release Checklist

Use this checklist before treating a decoder revision as release-ready.

## Required commands

- [ ] `python tests/test_ko_roundtrip.py --output results/ko_roundtrip_diagnostics.csv`
- [ ] `python tests/ko_decoder_stress_runner.py --cases data/ko_decoder_stress`
- [ ] `python tests/ko_decoder_realtext_spotcheck.py --limit 4 --sample --seed 42 --repeats 3`
- [ ] If available, run against the larger DB via `BRAILLE_MSDS_DB_PATH=<path> python tests/ko_decoder_realtext_spotcheck.py --limit 50 --sample --seed 42 --repeats 5`
- [ ] `python tests/ko_decoder_noisy_stress.py --cases data/ko_decoder_stress`
- [ ] `python -m pytest tests/test_ko_decoder_regressions.py tests/test_roundtrip_dispatch.py tests/test_en_roundtrip.py tests/test_braille_roundtrip.py -q`
- [ ] `python eval/run_e2e_eval.py --config eval/e2e_config.json --output results/e2e_eval_results.csv`

## Expected pass criteria

- [ ] Golden set stays at 45/45 and 1.0000 / 1.0000
- [ ] Stress corpus summary reports 27 cases / 0 failures
- [ ] Real-text repeated sample summary reports 0 failures
- [ ] Larger DB exploratory sample is reviewed explicitly; do not assume sample-DB success transfers to full production text
- [ ] Noisy-braille summary is reviewed for unexpected collapse versus prior runs
- [ ] Regression pytest suite passes cleanly
- [ ] E2E proposed path remains at 1.0000 across text/edit/structure and 0.00 rule violations

## Artifact check

- [ ] `results/ko_decoder_stress_results.csv`
- [ ] `results/ko_decoder_stress_summary.csv`
- [ ] `results/ko_decoder_realtext_spotcheck.csv`
- [ ] `results/ko_decoder_realtext_spotcheck_summary.csv`
- [ ] `results/ko_decoder_noisy_stress.csv`
- [ ] `results/ko_decoder_noisy_stress_summary.csv`
- [ ] `results/ko_roundtrip_diagnostics.csv`
- [ ] `results/e2e_eval_results.csv`

## Residual risk review

- [ ] Large real DB not yet sampled in this run
- [ ] Dense regulatory sections (notably sec-3 / sec-8 / sec-9 / sec-11 in exploratory runs) remain a priority risk area
- [ ] URL/slash-heavy and table-heavy cases still treated as residual risk unless separately tested
- [ ] OCR-like corruption not covered by the current decoder release lane

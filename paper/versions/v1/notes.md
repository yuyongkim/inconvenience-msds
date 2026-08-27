# v1 — 2026-05-27 — UAIS 제출 후보 (피드백 반영본)

## 한 줄 요약
피드백 (`paper/피드백.md`) 7개 항목 전부 반영한 첫 동결 버전. UAIS 즉시 제출 가능 상태.

## 들어 있는 것
- `manuscript.pdf` (10쪽, xelatex 컴파일)
- `manuscript.docx` (pandoc 변환)
- `cover_letter.md` (축약·톤다운 버전)
- `supplementary.zip` (12개 재현 파일)
- `main.tex` (IEEEtran 원본)
- `main_svjour3.tex` (Springer svjour3 동기화본)

## v1에 포함된 결정사항

### 데이터 수치 (검증 완료)
- chemicals: 48,966
- sections: 769,897 (DB) / 401,272 (released non-empty)
- text: 119.3M chars / braille: 232.3M cells
- per-chemical text: mean 2,436 / median 772 / std 2,431 / min-max 0-15,641
- char dist: Korean 77.2% / Latin 18.3% / Digit 4.5%
- cross-ref validation: 442/442 (100%) against hbcvt
- golden roundtrip: 45/45
- stress: 27/27 zero failures
- GHS: 147 codes (63 H + 84 P)
- CAS in KOSHA MSDS records: 13,445 distinct
- K-REACH: 47,344 / Food allergens: 19

### Figures (5개 inline)
1. System architecture (`fig_pipeline`)
2. Encoding example "메탄올"/"인화성" (`fig_encoding_example`)
3. Dataset stats (real data, bimodal histogram) (`fig_dataset_stats`)
4. Per-section coverage (`fig_section_coverage`)
5. Web UI (`fig_webui`)

### 구조 결정
- Abstract: Purpose / Methods / Results / Conclusion (UAIS 필수)
- Keywords: 6개
- Sec I-D Contributions: "design, implementation, public-release study" 명시
- Sec II 강화: braille for technical reading + accessibility theory framings
- Sec VII: Validated / Prospective 분리
- Sec VIII: Scope of Claims (Validated / Not yet validated / 왜 성립하는가) 신설
- Sec VIII: Maintenance and Update Model 신설
- Acknowledgments + Declarations (Funding/Competing/Ethics/Author/DataCode) 추가
- Figures 모두 `[H]` 인라인

### 검증 산출물
- `archive/verification/verify_numbers.py` → `verified_numbers.json`
- `archive/verification/verify_cross_reference.py`

## 사장님 직접 손볼 곳 (제출 직전)
- ORCID 등록 후 main.tex 21행 / main_svjour3.tex 28행 교체
- Reviewer 추천 2–3명 (선택)
- HuggingFace + GitHub 리포 공개 확인

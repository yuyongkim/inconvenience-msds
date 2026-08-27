# KOSHA-Braille

Korean chemical safety MSDS braille conversion pipeline + dataset.
IEEE Access 논문용 프로젝트.

## Paper Framing (중요)

**Infrastructure-grade accessibility** 관점이 논문의 핵심 논조.
"First large-scale dataset" 같은 novelty 자랑이 아니라:

- 정보 접근성은 **서비스**가 아니라 **인프라** — 점자블록·스크린도어·자막과 같은 범주
- 사용량(adoption volume)이 정당성의 척도가 아님 — **parity of access**가 척도
- "시각장애 화학자가 적어서 수요 없음" 반론 → 자기충족적 예언 (정보 없으니 진입 봉쇄, 진입자 없으니 정보 안 만듦)
- 법적 근거: UN CRPD Article 9 + 장애인차별금지법 제21조
- 2차 독자(국회 보좌진, 노동감독관, 변호사, 기자, 시민단체) 포함 시나리오가 중요
- Extensibility (Section VIII) 반드시 명기 — 의약품/식품/K-REACH/법률 등으로 확장 가능한 템플릿

논문 어느 섹션을 수정하든 이 프레이밍 일관성 유지 필수.

## Quick Reference

- **DB**: `G:/MSDS/data/terminology.db` (SQLite, 48,966 chemicals, 769,897 MSDS sections)
- **Web**: `cd web/backend && uvicorn server:app --host 0.0.0.0 --port 8000 --reload`
- **Tests**: `python -m pytest tests/`
- **Full pipeline**: `python pipeline/run_pipeline.py <input.brf>`
- **Bulk MSDS→braille**: `python scripts/msds_bulk_braille.py`
- **HF dataset export**: `python scripts/export_hf_dataset.py`
- **Paper compile**: `cd paper && pdflatex main.tex`

## Architecture

```
EN Braille (.brf/.txt) → decode → correct → structure → translate → KR Braille
KR MSDS (KOSHA DB)     → extract XML → KR text → KR Braille (직접 점역)
```

### pipeline/ (13 modules)

| Module | Role |
|--------|------|
| `loader.py` | BRF/Unicode braille file loader, page/line parsing |
| `decoder.py` | Braille→English text (UEB G1/G2, capital indicator 처리) |
| `encoder.py` | English text→braille (simplified UEB, 테스트용) |
| `corrector.py` | Rule-based noise corrector (7 noise types) |
| `structure.py` | Document structure detector (P/L/T/M blocks) |
| `translator.py` | EN→KR translator (Google Translate free tier) |
| `ko_braille.py` | Korean text→Korean braille (2017 한국 점자 규정) |
| `ko_braille_decoder.py` | Korean braille→Korean text (roundtrip 검증용) |
| `assembler.py` | JSON/Markdown output formatter |
| `embosser.py` | BRF/Unicode/PDF output format generator |
| `brf_tables.py` | BRF ASCII↔Unicode braille mapping tables |
| `ueb_g2_tables.py` | UEB Grade 2 contraction tables |
| `run_pipeline.py` | CLI entry point, 6-stage orchestration |

### scripts/ (주요)

| Script | Role |
|--------|------|
| `msds_bulk_braille.py` | 49K chemicals bulk conversion (3분) |
| `validate_kr_braille.py` | KR braille quality validation (coverage, roundtrip, rule violations) |
| `ghs_braille.py` | GHS H/P statements→braille lookup |
| `export_hf_dataset.py` | HuggingFace JSONL export (48,966 records) |
| `domain_expansion.py` | KISCHEM/FDA/식품 알레르겐 braille export |
| `intl_expansion.py` | CAS 기반 국제 화학물질 cross-reference |

### eval/ (평가)

| Module | Role |
|--------|------|
| `run_e2e_eval.py` | Baseline vs Proposed E2E 비교 (3 documents) |
| `run_noise_correction_eval.py` | Noise corrector 성능 평가 |
| `rule_checker.py` | Korean braille 규정 위반 검사 (5 rules) |
| `similarity.py` | Edit similarity, ChrF, token F1 metrics |

### web/

- `backend/server.py` — FastAPI, SQLite DB 직접 연결, lxml XML 파싱
- `frontend/index.html` — 단일 HTML, 한국어 UI, 검색/조회/다운로드

## DB Schema (terminology.db)

주요 테이블:
- `chemical_terms` — external_id, name, cas_no, name_en
- `msds_details` — chem_id, section_no (1-16), xml_data

## Dependencies

Python 3.10+. No requirements.txt — 주요 패키지:
- `lxml` — XML parsing (MSDS data)
- `deep-translator` — Google Translate (free, no API key)
- `fastapi`, `uvicorn` — web service
- `reportlab` — PDF braille output
- Standard library only for core pipeline

## Key Numbers

- 48,966 chemicals, 0 errors
- 98.1% encoding coverage
- G1 roundtrip 100% (45/45)
- Noise corrector hurt rate 0/748
- HF dataset: `data/hf_dataset/train.jsonl` (943MB, 48,966 records)

## Conventions

- Korean braille follows 2017 한국 점자 규정 (문화체육관광부 고시)
- Mixed script: 로마자 표시(⠴), 수표(⠼), 대문자 표시(⠠)
- GHS pictogram codes (GHS01-09) → descriptive Korean text로 변환
- MSDS sections 1-16 follow KOSHA standard ordering
- Output formats: Unicode (.txt), BRF (.brf), PDF, JSONL

## Data Locations

| Path | Contents |
|------|----------|
| `data/hf_dataset/train.jsonl` | HuggingFace dataset (48,966 chemicals) |
| `data/braille/en/` | English braille test samples |
| `data/braille/ref_converter/` | External Korean braille reference impl |
| `data/domain_expansion/` | KISCHEM, FDA, food allergen JSONL |
| `data/e2e/` | E2E evaluation documents (d01-d03) |
| `results/msds/` | Bulk conversion results, GHS stats |
| `paper/` | IEEE Access LaTeX source + figures |


## 개인 지식 위키 참조
배경 지식, 프로필, 관련 프로젝트 정보가 필요하면 `C:\Users\USER\Desktop\LLM Wiki`를 참조하세요.
- 소유자 프로필: `LLM Wiki/identity/profile.md`
- 전체 프로젝트 목록: `LLM Wiki/projects/_index.md`
- 프롬프트 모음: `LLM Wiki/tools/prompts/_index.md`

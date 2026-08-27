# 제출 가이드

**현재 버전: v2** (`VERSION` 파일 참조 · 이력은 `CHANGELOG.md`)

## 이 폴더 (`paper/original_article/`) — Original Article 제출용 파일만 (항상 최신 = v{현재})

| 파일 | 용도 |
|---|---|
| `manuscript.pdf` | **메인 본문** (10쪽, UAIS/IEEE Access/TACCESS 전부 PDF 받음) |
| `manuscript.docx` | Word 백업본 (pandoc 변환 — 표·수식 미세 깨짐 가능, 검수 필요) |
| `cover_letter.md` | UAIS Editorial Manager의 cover-letter 입력란에 본문 그대로 복사 |
| `supplementary.zip` (51 KB) | Supplementary Material 항목에 업로드 |
| `HOW_TO_SUBMIT.md` | 이 파일 |

---

## 제출 순서 (UAIS 기준)

1. https://www.editorialmanager.com/uais/ 접속 → Author Login → Submit New Manuscript
2. ORCID 입력 (없으면 https://orcid.org 에서 5분 만에 발급)
3. 업로드:
   - Manuscript → `manuscript.pdf`
   - Cover Letter → `cover_letter.md` 내용 복사·붙여넣기
   - Supplementary → `supplementary.zip`
4. Article Type: **Original Article**
5. Suggested Reviewers (선택): 2–3명 — 한국 점자 / 접근성 정책 / 화학정보 분야
6. Submit

---

## `../versions/` 폴더 — 버전 스냅샷

| 폴더 | 내용 |
|---|---|
| `../versions/v1/` | 제출 파일 5종 + `main.tex` + `main_svjour3.tex` + `notes.md` |
| `../versions/v2/` 등 | 향후 수정마다 신규 생성 |

새 버전 만드는 절차: `original_article/`의 현재 파일을 `../versions/v{N+1}/`에 복사 → 그 폴더에 `notes.md` 추가 → `VERSION` 갱신 → `CHANGELOG.md`에 항목 추가.

## `../archive/` 폴더 — 모든 작업 산출물 (제출 후 사용)

| 폴더 | 안에 뭐 있나 | 언제 쓰나 |
|---|---|---|
| `../archive/tex_source/` | `main.tex` + 5개 figure PDF/PNG | 본문 수정·재컴파일 필요 시 |
| `../archive/tex_build/` | `main.aux/log/out` | LaTeX 빌드 부산물 (참고용) |
| `../archive/uais_reformat/` | Springer svjour3 클래스로 재포맷한 main.tex + refs.bib + figures + README | UAIS accepted 후 양식 변환 제출 요구 시 |
| `../archive/verification/` | `verify_numbers.py`, `verify_cross_reference.py`, `verified_numbers.json` | 리뷰어가 수치 의심 시 재실행 근거 |
| `../archive/figure_generators/` | `gen_fig_*.py` (5개) | Figure 다시 만들 때 |
| `../archive/supplementary_unzipped/` | `supplementary.zip` 펼친 12개 파일 | zip 안 보고 파일 직접 보고 싶을 때 |
| `../archive/drafts/` | `ieee_access_draft.md`, `dataset_stats.json` | 옛 마크다운 초안 / 옛 통계 (현재는 verified_numbers.json이 권위) |

---

## 제출 직전 체크리스트

- [ ] `manuscript.pdf` 1쪽 저자 블록에 본인 ORCID 들어갔는지 (없으면 `../archive/tex_source/main.tex` 수정 후 재컴파일)
- [ ] `cover_letter.md` 본문 톤·내용 본인 검토
- [ ] HuggingFace 데이터셋 페이지(`Yuyongkim/inconvenience-msds`) 공개 상태 확인
- [ ] GitHub 리포지토리(`yuyongkim/inconvenience-msds`) 공개 상태 확인
- [ ] Reviewer 추천 명단 준비 (선택, 그러나 강력 권장)

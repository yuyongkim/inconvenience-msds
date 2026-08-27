# Changelog

본 폴더(`paper/original_article/`)의 Original Article 제출 패키지 버전 이력. 각 버전 스냅샷은 `../versions/v{N}/` 에 보존.

새 수정마다 (a) 본 파일에 항목 추가, (b) `../versions/v{N+1}/` 디렉토리 생성, (c) 5개 파일(`manuscript.pdf`, `manuscript.docx`, `cover_letter.md`, `supplementary.zip`, `main.tex`, `main_svjour3.tex`, `notes.md`) 복사, (d) `VERSION` 갱신.

## 명명 규칙
- `v1`, `v2`, `v3` ... — 메이저 수정 단위 (구조 변경, 새 섹션 추가, 수치 재계산, 리뷰어 응답 등)
- 같은 버전 내 미세 수정(타자 오류, ORCID 추가 등)은 새 버전 만들지 않고 그 자리에서 덮어쓰기

## 버전별 의미
- **submission**: 제출 직전 동결본 (실제 Editorial Manager에 올라간 파일과 동일)
- **revision**: 리뷰어 응답 후 재제출본
- **internal**: 외부 제출 없이 내부 정리/실험용

---

## v2 — 2026-05-27 — **submission ready** (피드백 delta 반영)

### 한 줄
v1에 대한 추가 피드백("submit-ready에 근접, minor polish 후 제출 권장")의 3가지 잔여 항목 반영. 제출 권장 상태.

### v1 → v2 변경 (3개만)
- **Cover letter** — "I would be glad to suggest reviewers on request." 삭제 (피드백: 더 건조하게)
- **Conclusion 끝 단락 신설** — scope boundary 재확인 + Maintenance and Update Model(Sec~\ref{sec:maintenance}) 참조. 피드백: maintenance commitment가 Conclusion에서도 한 눈에 보여야 함.
- **Declarations 가시성 확인** — 변경 없음, 이미 Springer convention 대로 \section*{} 위계에 배치됨.

### 피드백 평가 (v2 기준 인용)
> "이전 평가 대비 이번 개정은 실질적 개선이 맞고, 특히 abstract·포지셔닝·cover letter가 좋아졌습니다. 지금 남은 핵심 리스크는 user study 부재 하나로 압축됐으며, 그조차도 이제는 '설명되지 않은 약점'이 아니라 '명시적으로 관리된 한계'입니다. 제 기준에선 제출해도 되는 버전입니다."

### 분량 (v1과 거의 동일)
10쪽 / PDF 326 KB / DOCX 167 KB / supplementary.zip 51 KB

### v2 후속 추가 (in-place, 버전 안 올림)
- **ORCID 적용** — `0009-0006-4842-666X`
- **한국어 본문** — `manuscript_ko.pdf` / `manuscript_ko.docx` / `archive/tex_source/main_ko.tex`. 학술 격식체 번역, 동일 figure·표·참고문헌 키 사용.
- **커버레터 docs/pdf 추가** — `cover_letter.docx`, `cover_letter.pdf` (영어)
- **한국어 커버레터** — `cover_letter_ko.md` / `cover_letter_ko.docx` / `cover_letter_ko.pdf`

---

## v1 — 2026-05-27 — **submission candidate** (UAIS 1순위)

### 한 줄
피드백(`paper/피드백.md`) 반영 1차 동결본. UAIS Editorial Manager에 그대로 제출 가능.

### 핵심 변경 (v0=git baseline 대비)
- **수치 전수 검증** — 6,046/5,934/1,435/2,241/10,490 → 실제 2,436/772/2,431/0/15,641 / 76.3-16.6-7.1% → 77.2-18.3-4.5% / 74,494 CAS 출처 오류 → 13,445 (KOSHA distinct) / 769,897 sections → "769,897 source-DB rows / 401,272 released non-empty" 양쪽 표기 / 7,189 KISCHEM "exported" → "DB n=7,189, 100건 demo export"
- **Figure 5개로 확장 + 본문 inline** — 신규 Fig 2 (encoding example), Fig 4 (section coverage) 추가. 기존 Fig 3 (dataset stats) 합성 데이터에서 실데이터로 교체.
- **검증 스크립트 추가** — `verify_numbers.py`, `verify_cross_reference.py`, `verified_numbers.json`
- **Declarations 섹션 신설** — Acknowledgments / Funding / Competing Interests / Ethics / Author Contributions / Data and Code Availability
- **Abstract 구조화** — Purpose / Methods / Results / Conclusion (UAIS 필수)
- **Keywords 축소** — 10 → 6
- **Sec II Related Work 강화** — braille for technical reading 단락 + accessibility theory framings 추가
- **Sec VII Extensibility 재구성** — Validated (KOSHA/MSDS, 식품 알레르겐, KISCHEM 100건, CAS 매핑) vs Prospective (의약품 전체, K-REACH, 법률, 타 규제권) 분리
- **Sec VIII 신설**: Scope of Claims (Validated / Not yet validated / 왜 (a)-(c) 없이 성립하는가) + Maintenance and Update Model
- **Sec I-D Contributions 첫 문장에 "design, implementation, public-release study" 명시** — usability paper 오해 차단
- **Cover letter 축약·톤 다운** — 20-30% 단축, 단정적 표현 제거, Limitation 1문단 3문장
- **svjour3 (Springer) 버전 동기화** — `archive/uais_reformat/main.tex`

### 분량
- 10쪽 / xelatex 컴파일 / 호환성: pdf+docx+svjour3
- supplementary.zip 51 KB / 12 파일

### 제출 직전 사장님 직접 손볼 곳
- ORCID 등록 후 `archive/tex_source/main.tex:21` + `archive/uais_reformat/main.tex:28` placeholder 교체
- Reviewer 추천 2–3명 (선택)
- HuggingFace `Yuyongkim/inconvenience-msds` 및 GitHub `yuyongkim/inconvenience-msds` 공개 상태 확인

---

## v0 — pre-versioning (참고용)

git baseline 커밋 `f36a1f4` ("Initial release: inconvenience-msds"). 본문 내 수치가 일부 잘못된 상태로, 제출용으로 사용된 적 없음. 본격적인 검증·재구성 작업이 v1에서 이루어짐.

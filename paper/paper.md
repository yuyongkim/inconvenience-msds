# Paper submission plan

Status as of 2026-04-14.

---

## 1. Target venue

**Universal Access in the Information Society (UAIS)** — Springer, SCIE

| 항목 | 내용 |
|------|------|
| APC | **$0** (구독 트랙; OA 선택 시 $3,190 — 선택하지 않음) |
| Impact Factor | ~3.0, SCIE 인덱스 |
| 마감 | 상시 투고 |
| User study 요구 | 없음 |
| 편집 방향 | 정보 사회의 보편적 접근성 — infrastructure framing과 정확히 일치 |
| 투고 시스템 | Springer Editorial Manager |
| 템플릿 | Springer Nature LaTeX (내용 변경 없음, 포맷만 전환) |

**왜 UAIS인가:**
- UAIS 리뷰어들은 접근성을 인프라로 이해하는 커뮤니티 — CRPD/장차법 근거, self-fulfilling exclusion 논리가 낯설지 않음
- 현재 논문 구조(접근성 인프라 + 법/권리 + 시스템 + 코퍼스)가 UAIS 요구사항과 완전 일치 → 내용 수정 불필요
- 상시 투고 → 지금 바로 처리하고 트랙3로 전환 가능

**탈락한 옵션:**

| 옵션 | 탈락 사유 |
|------|----------|
| ~~IEEE Access~~ | APC $2,160 |
| ~~Language Resources and Evaluation~~ | NLP 모델 성능 지표 요구 — 프레이밍 충돌 |
| ~~ACM TACCESS~~ | APC $1,450 (2026 OA 전환), user study 사실상 필수 |
| ~~ASSETS 2026 full paper~~ | 마감 4/22 (현실적 불가), user study 기대 |
| ~~arXiv~~ | 신규 제출자 endorsement 필요 — 현재 불가 |

**프리프린트 (병행):** **TechRxiv** (IEEE 운영, endorsement 불필요, 즉시 DOI) — 투고 전 업로드하여 우선일자 확보

---

## 2. Paper metadata

| Field | Value |
|-------|-------|
| Title | *KOSHA-Braille: Infrastructure-Grade Accessibility for Korean Chemical Safety Information* |
| Article type | Research Article |
| Author | Yu Yong Kim, University of Wisconsin–Madison |
| Email | ykim288@wisc.edu |
| ORCID | **0009-0006-4842-666X** |
| Keywords | Accessibility infrastructure, braille, chemical safety, MSDS, Korean braille, visually impaired, GHS, occupational health, disability rights, dataset |
| APC | $0 (구독 트랙) |

---

## 3. UAIS 투고 체크리스트

| 항목 | 상태 | 비고 |
|------|------|------|
| Springer Nature LaTeX 템플릿 | ✅ | sn-jnl.cls, 컴파일 완료 (20p, 1.6MB) |
| ORCID 등록 및 공개 | ✅ | 0009-0006-4842-666X |
| 제목 / 초록 / 키워드 | ✅ | v0.2 기준 |
| 본문 섹션 (I–X) | ✅ | v0.2 기준 완성 |
| References (Springer 형식) | ✅ | manual thebibliography, 컴파일 정상 |
| 그림 3개 (PDF) | ✅ | `figures/` 폴더에 위치 |
| 저자 기여 선언 | ✅ | CRediT 7개 역할 명시 |
| 이해충돌 선언 | ✅ | "The author declares no conflict of interest." |
| 데이터 가용성 선언 | ✅ | HF + GitHub URL 포함 |
| AI 사용 공시 | ✅ | Claude (Anthropic) 문구 추가 완료 |
| 구독 트랙 명시 선택 | ❌ | 투고 시 OA 옵션 **선택하지 않음** 확인 필수 (제출 시 직접) |

**투고 차단 요소:** 없음 (ORCID 완료).

---

## 4. 내용 준비 상태

| 섹션 | 상태 | 비고 |
|------|------|------|
| Abstract | ✅ | 232.3M 셀 수치 통일 완료 (v0.1) |
| I. Introduction | ✅ | CRPD Art.9 + 장차법 Art.21 근거 |
| II. Related Work | ✅ | Hamraie, Blackwell, Bennett-Keyes |
| III. System Architecture | ✅ | 파이프라인 + 인코딩 룰 + 테이블 2개 |
| IV. Dataset Description | ✅ | 통계 + GHS 테이블 + 스키마 + 릴리스 정보 |
| V. Validation | ✅ | 결정론적 정당화 단락 추가 완료 (v0.1) |
| VI. Experiments | ✅ | Korean round-trip 메인(Table IV), 평가 기준 매핑 테이블 추가 완료 (v0.1) |
| VII. Reference Deployment | ✅ | 7개 API 엔드포인트 |
| VIII. Extensibility | ✅ | 5개 축 |
| IX. Discussion | ✅ | user study 방어 강화 완료 (v0.1) |
| X. Conclusion | ✅ | "cannot enter a profession" 마무리 |
| References | ✅ | 20개, [9] 충돌 해결 완료 (v0.1) |

---

## 5. 리뷰어 예상 반응

### 우호적 리뷰어

- 48,966개 점자 코퍼스 — 사실적 최초
- infrastructure framing + CRPD/장차법 법적 근거 — UAIS 커뮤니티에서 익숙한 논리
- 결정론적 인코더 + 독립 구현 교차검증 100% — 재현성 높음
- Extensibility 섹션 — "한국에만 적용 가능" 반론 선제 차단

### 회의적 리뷰어

1. **User study 부재** — 현재 IX-D에서 "infrastructure precedes user study" 논리로 방어. curb cut 사례 명시.
2. **Grade 1 only** — 한계로 명시, determinism 요구사항과 trade-off 설명.
3. **인프라 프레이밍이 수사적 방어로 읽힐 수 있음** — 아티팩트(48,966개 실제 코퍼스)가 가장 강한 반론.

---

## 6. 투고 전 액션 리스트

### 필수 (투고 차단)

- [x] **ORCID 등록** — 0009-0006-4842-666X
- [x] AI 사용 공시 문구 결정 — Claude (Anthropic) 명시
- [x] IEEEtran → **Springer Nature LaTeX 템플릿** 전환
- [x] References Springer 형식 (manual thebibliography)
- [x] CRediT author statement 추가
- [x] 이해충돌 선언 추가
- [ ] 투고 시 OA 트랙 **비선택** 확인 (제출 시 직접)

### 권장 (투고 전)

- [ ] **TechRxiv** 프리프린트 업로드 (우선일자 + HF dataset card 링크)
- [ ] 공공누리 제1유형 재배포 조건 공식 확인

### 투고 후 (리뷰 대응 시)

- [ ] 소규모 user comprehension study (N=3–5, refreshable display)
- [ ] 한국시각장애인연합회 또는 KOSHA 접근성 담당 비공식 확인서

---

## 7. 타임라인

| 시점 | 액션 |
|------|------|
| 이번 주 | ORCID 등록, Springer 템플릿 전환, References 스타일 변환 |
| 이번 주 | TechRxiv 프리프린트 업로드 |
| 이번 주 말 | UAIS Editorial Manager 투고 |
| +6–10주 | 1차 리뷰 수령 |
| 리뷰 후 | 최소 대응, 트랙3 유지 |

투고 직후 이 프로젝트는 유지보수 모드 전환 — 트랙3 집중.

---

## 8. 파일 현황

```
paper/
├── draft.md   # 논문 본문 (MD, ground truth) — v0.1
├── main.tex               # LaTeX 소스 (IEEEtran → Springer 전환 필요)
├── supplement.md          # 보충 자료
├── paper.md               # 이 파일
├── figures/
│   ├── fig_pipeline.pdf/png
│   ├── fig_dataset_stats.pdf/png
│   ├── fig_webui.pdf/png
│   ├── gen_fig_*.py
│   └── dataset_stats.json
└── (리뷰 후 생성)
    ├── archive/           # draft_v0.md 등 스냅샷
    └── reviews/           # r1_comments.md, r1_response.md
```

---

Sources:
- [UAIS Journal — Springer](https://link.springer.com/journal/10209/how-to-publish-with-us)
- [TechRxiv — IEEE preprint server](https://www.techrxiv.org/)
- [Springer Nature LaTeX template](https://www.springernature.com/gp/authors/campaigns/latex-author-support)

# v2 — 2026-05-27 — UAIS 제출 후보 (피드백 delta 반영본)

## 한 줄 요약
v1에 대한 추가 피드백("submit-ready에 근접, minor polish 후 제출 권장")의 3가지 잔여 항목 반영한 동결본. **제출 권장 상태.**

## v1 대비 변경 (3개만)

### 1. Cover letter
- 삭제: "I would be glad to suggest reviewers on request."
- 이유: 피드백 — 이 줄은 무난하지만 더 건조하게 가려면 빼는 게 낫고, 본인도 삭제·간소화를 약간 선호한다고 명시. 커버레터는 이미 짧고 톤이 차분해서 제거 시 더 깔끔.

### 2. Conclusion 끝에 scope-boundary + maintenance commitment echo 단락 신설
- 추가된 문단: "We close by underscoring the scope boundary this paper holds throughout: the contribution is the design, validation, and public release of accessibility infrastructure; it is not a claim about end-user reading performance. Maintenance of that infrastructure beyond the present release is committed to under the model described in Section~\ref{sec:maintenance}..."
- 이유: 피드백 — Conclusion에서 maintenance가 한눈에 안 보일 수 있다는 우려. Discussion의 Maintenance and Update Model 단락은 그대로 두고, Conclusion에서 한 번 더 참조 + scope boundary 재확인.

### 3. Declarations 가시성 (변경 없음, 확인만)
- 현재 상태: \section*{Acknowledgments} → \section*{Declarations} (Funding / Competing Interests / Ethics and Consent / Author Contributions 4개 subsection) → \section*{Data and Code Availability}
- 이미 Springer convention 그대로. 추가 작업 없음.

## v2에 포함된 (v1과 공유) 모든 결정사항
v1 notes 참조. 수치·figure·구조·svjour3 동기화·검증 스크립트 모두 동일.

## 분량
- 영어 manuscript: 10쪽 / PDF 326 KB / DOCX 167 KB
- 한국어 manuscript: PDF 466 KB / DOCX 168 KB (학술 격식체 번역, 동일 figure·표·참고문헌 키 사용)
- 영어 cover letter: MD + DOCX (11 KB) + PDF (15 KB)
- 한국어 cover letter: MD + DOCX (12 KB) + PDF (64 KB)

## 제출 직전 사장님 직접 손볼 곳
- ~~ORCID 등록 후 main.tex 21행 / main_svjour3.tex 28행 placeholder 교체~~ → **완료** (2026-05-27, 0009-0006-4842-666X)
- HuggingFace + GitHub 리포 공개 상태 확인

## 피드백 평가 (v2 기준)
인용: "이전 평가 대비 이번 개정은 실질적 개선이 맞고... 제 기준에선 제출해도 되는 버전입니다."

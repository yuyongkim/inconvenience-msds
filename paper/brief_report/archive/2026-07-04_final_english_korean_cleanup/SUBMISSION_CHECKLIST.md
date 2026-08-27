# UAIS Brief Reports Resubmission Checklist

## 산출물

- `submission/manuscript_brief_report_final.docx` - Brief Report article type 표기 포함 원고. 최신 ACK 반영본.
- `submission/cover_letter_brief_report.docx` - 편집장 제안에 따른 Brief Reports 재제출임을 명시.
- `submission/title_page_brief_report.docx` - 저자 정보, ORCID, corresponding author 포함.
- `submission/supplementary.zip` - 기존 보충자료 사본.
- `source/` - 원고 재생성용 LaTeX/Markdown/figure/BibTeX 소스. SNAPP에는 업로드하지 않음.
- `korean_reference/` - 한글 참고본. SNAPP에는 업로드하지 않음.

## 최신 피드백 반영

- 초록과 서론을 Brief Report 톤으로 재작성: 철학적 framing 축소, corpus/encoder/release 중심으로 재배열.
- Extensibility forecast 축소: 구현되지 않은 추가 도메인은 일반적인 future target으로만 표기.
- Discussion 압축: user study 부재 방어를 별도 장광설이 아니라 scope boundary와 follow-up study로 정리.
- Maintenance model 압축: versioned release, reproducible rebuild path, open scripts만 유지.

## SNAPP 입력 체크

- Article Type: `Brief Reports` 선택.
- 이전 제출 ID: `aae028f8-e8f0-43c1-888c-c986dfe01198`를 cover letter 또는 포털 메모에 기재.
- Editor suggestion: Brief Reports 카테고리 재제출임을 명시.
- Abstract: Purpose / Methods / Results / Conclusion 구조 유지, 150-250 words 범위 확인.
- Keywords: 4-6개 입력. 현재 6개.
- Declarations: Funding, Competing Interests, Ethics and Consent, Author Contributions 입력.
- Data Availability: HuggingFace dataset, GitHub repository, Korea Public Data Portal 원천 데이터, CC BY 4.0 / MIT license 입력.
- References: 원고 docx에서 대괄호 숫자 인용과 숫자순 참고문헌 목록을 최종 proof에서 재확인.
- Source files: `submission/` 안의 docx 3종과 보충자료 zip만 업로드.

## 최종 확인 완료

- UAIS 공식 Submission guidelines 기준 structured abstract 150-250 words, 4-6 keywords, title page 정보, declarations, 숫자 대괄호 인용을 현재 `submission` 원고에서 확인 완료: https://link.springer.com/journal/10209/submission-guidelines
- Brief Reports 전용 공개 분량 제한은 UAIS 공식 Submission guidelines에 별도 항목으로 표시되지 않음(확인일: 2026-07-03).
- User study 부재는 본문에서 scope boundary와 future work로 관리됨. 커버레터는 현재처럼 짧게 유지.

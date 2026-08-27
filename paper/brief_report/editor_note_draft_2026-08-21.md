# 편집자 통지 초안 — 2026-08-21 (발송 전, 검토용)

수신: proofeditor@springernature.com (cc: priya.verma@springernature.com)
건: 10.1007/s10209-026-01381-0 / 10209_2026_1381_Article

---

Dear Editor,

While reviewing the proofs I must disclose a matter that goes beyond typesetting.

After submission I audited the encoder rule by rule against the source standard
(『2017 개정 한국 점자 규정』 한글 점자 규정 해설, National Institute of Korean
Language, doc. 2018-01-02) by extracting the 1,238 worked print/braille example
pairs typeset in the standard's own braille font and comparing them mechanically
with the encoder's output.

The audit found that the encoder, as described in the accepted manuscript, did
not implement two mandatory provisions:

  - Article 2, which prescribes that an initial 'ㅇ' is *not* written, and
    defines that omission as the standard (정자) form. The encoder wrote a cell
    for it. This affects 24.2% of Hangul syllables in the corpus.
  - Articles 12-18, the abbreviation (약자) and contraction (약어) tables. None
    were implemented.

The manuscript therefore overstates one claim: that the encoder is "aligned with
the 2017 Korean Braille Standards". At the time of submission it implemented the
jamo-level dot tables correctly, but not the orthographic rules built on them.
Measured against the standard's own worked examples, the submitted encoder
matched 15 of 475; the corrected encoder matches 275 of 475.

Two consequences follow, and I would like your guidance on how you wish them
handled.

1. The cross-validation result reported in Table 6 ("100% agreement over 442
   cross-reference test cases" against an independent open-source converter) was
   correctly measured, but it is now clear that the comparison operates at the
   jamo-transcription level: the reference implementation likewise writes the
   initial 'ㅇ' and does not use abbreviations. Agreement between two
   implementations sharing the same omission is weaker evidence of standards
   compliance than the manuscript presents it to be. Re-running the same harness
   with the corrected encoder yields 36/41, 0/45 and 2/356 on the three test
   sets, the divergences falling entirely on Article 2 and Articles 12-18.

2. The quantitative descriptions of the released artifact (232.3 million braille
   cells; mean braille:text ratio 1.95) describe the artifact as submitted and
   remain accurate for that version. Correcting the encoder reduces the corpus to
   209.7 million cells at a ratio of 1.65.

I see two ways forward and defer to you:

  (a) Publish as accepted, with the released dataset and code pinned to the
      version the manuscript describes, and narrow only the compliance sentence
      so that it claims what was actually verified (jamo-level dot tables and
      agreement with an independent implementation) rather than full compliance
      with the 2017 standard. The corrected encoder would then be released as a
      subsequent version and reported separately.

  (b) Update the manuscript to describe the corrected encoder. This changes the
      headline corpus figures, one figure (Fig. 2, whose worked examples change
      shape because abbreviations occupy a single cell), and the framing of the
      cross-validation, and would require editorial review.

I recognise (b) is a scientific-content change at proof stage. I raise it because
the compliance claim is central to the report's contribution, and I would rather
it be accurate than early.

The audit is fully documented and reproducible; I can supply the extraction
harness, the per-article comparison, and a point-by-point list of the affected
sentences on request.

Yours sincerely,
Yuyong Kim

---

## 근거 파일

- `notes/2026-08-13-regulation-audit.md` — 감사 전문, 항별 상태
- `paper/brief_report/errata_2026-08-14.md` — 제출본 대비 정정 목록
- `data/standards/2017_한글점자규정해설_국립국어원.pdf` — 원본 표준 (SHA-256 기록됨)
- `tests/ko_decoder_residual_classify.py` — 남은 왕복 불일치 분류

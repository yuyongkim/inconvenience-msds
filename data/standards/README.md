# Braille standards — primary sources

Authoritative documents the encoder is checked against. Keep these here so any
dot-pattern claim can be traced to a page in a published standard rather than to
a secondary source or a model's recollection.

## 2017_한글점자규정해설_국립국어원.pdf

| | |
|---|---|
| Title | 『2017 개정 한국 점자 규정』 한글 점자 규정 해설 |
| Publisher | 국립국어원 (National Institute of Korean Language) |
| Document no. | 국립국어원 2018-01-02 |
| 발간등록번호 | 11-1371028-000702-01 |
| Original file | 한글점자규정해설서_최종인쇄본.hwp |
| Pages | 146 |
| SHA-256 | `a7760df7312424f3662af492a409c0f010d50fa0c82ddd91d26565dcdf1ab0b4` |
| Retrieved | 2026-08-12 from `https://nise.go.kr/onmam/openapi/fileDown.do?fileSn=RkeU-d5_wdDcx1xjbUrhoQ` (국립특수교육원 미러) |
| Also listed at | https://www.korean.go.kr/front/etcData/etcDataView.do?mn_id=46&etc_seq=603 |

### Reading the braille in this PDF

Braille is set in the `HSBRL01` font, so the text layer yields **braille ASCII**,
not Unicode braille. Convert with `pipeline/brf_tables.ASCII_TO_BRAILLE`:

```python
from pipeline.brf_tables import ASCII_TO_BRAILLE as A
"".join(A[c] for c in "8'")   # 여는 소괄호 -> ⠓⠄
```

### Punctuation entries verified against `pipeline/ko_braille.py`

| 부호 | 항 | 규정 (braille ASCII) | 규정 (점형) | 인코더 | 일치 |
|---|---|---|---|---|---|
| 붙임표 `-` | — | `-` | ⠤ (3-6) | ⠤ (3-6) | 예 |
| 여는 소괄호 `(` | 제54항 | `8'` | ⠓⠄ (1-2-5 · 3) | ⠤ (3-6) | **아니오** |
| 닫는 소괄호 `)` | 제54항 | `,0` | ⠠⠚ (6 · 2-4-5) | ⠤ (3-6) | **아니오** |
| 여는 중괄호 `{` | 제55항 | `81` | ⠓⠁ (1-2-5 · 1) | 미구현 | — |
| 닫는 중괄호 `}` | 제55항 | `"0` | ⠐⠚ (5 · 2-4-5) | 미구현 | — |
| 여는 대괄호 `[` | 제56항 | `82` | ⠓⠃ (1-2-5 · 1-2) | 미구현 | — |
| 닫는 대괄호 `]` | 제56항 | `;0` | ⠰⠚ (5-6 · 2-4-5) | 미구현 | — |

제54항 해설이 개정 사유를 밝히고 있다.

> 소괄호 점형은 이번 『개정 한국 점자 규정』(2017)에서 많은 논의 끝에 개정되었다.
> 이는 ⠤이 소괄호, 붙임표, 줄표 등에서 다양하게 사용되어 여러 예외 규정이 생기는 등
> 혼동을 일으켜 왔고, 소·중·대괄호의 점형을 모두 중·하단 점형 두 칸으로 통일하여
> 표기함으로써 일관성을 유지하기 위함이다.

즉 현재 인코더의 단일 ⠤ 표기는 **개정 전 형태**이며, 2017 개정이 없앤 바로 그
혼동(괄호·붙임표 구분 불가)을 그대로 재현한다.

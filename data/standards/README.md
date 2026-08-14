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

Braille is set in the `HSBRL01` font, so the text layer yields **braille ASCII**
(NABCC), not Unicode braille.

`pipeline/brf_tables.ASCII_TO_BRAILLE` **cannot** be used to read it: that table
maps the ten digits to the letter cells `a`–`j` (`'8' -> ⠓`), while braille ASCII
maps them to the lower cells (`'8' -> ⠦`, 2-3-6). 제56항이 그 자리에서 점수를
직접 밝히고 있어 어느 쪽인지 가려진다.

> 제56항 여는 대괄호(〔 )는 `8'`(2-3-6점, 3점)으로, 닫는 대괄호( 〕)는 `,0`(6점,
> 3-5-6점)으로 적는다. *(2006년판 조문. 2017년판은 대괄호를 `82`/`;0`으로 옮겼다.)*

즉 `8` = 2-3-6 = ⠦, `'` = 3 = ⠄, `,` = 6 = ⠠, `0` = 3-5-6 = ⠴이다.

### Punctuation entries verified against `pipeline/ko_braille.py`

| 부호 | 항 | 규정 (braille ASCII) | 규정 (점형) | 인코더 | 일치 |
|---|---|---|---|---|---|
| 붙임표 `-` | 제59항 | `-` | ⠤ (3-6) | ⠤ | 예 |
| 마침표 `.` | 제44항 | `4` | ⠲ (2-5-6) | ⠲ | 예 |
| 물음표 `?` | 제45항 | `8` | ⠦ (2-3-6) | ⠦ | 예 |
| 느낌표 `!` | 제46항 | `6` | ⠖ (2-3-5) | ⠖ | 예 |
| 쉼표 `,` | 제47항 | `"` | ⠐ (5) | ⠐ | 예 |
| 쌍점 `:` | 제49항 | `"1` | ⠐⠂ (5 · 2) | ⠐⠂ | 예 |
| 쌍반점 `;` | 제50항 | `;2` | ⠰⠆ (5-6 · 2-3) | ⠰⠆ | 예 |
| 여는 소괄호 `(` | 제54항 | `8'` | ⠦⠄ (2-3-6 · 3) | ⠦⠄ | 예 |
| 닫는 소괄호 `)` | 제54항 | `,0` | ⠠⠴ (6 · 3-5-6) | ⠠⠴ | 예 |
| 여는 중괄호 `{` | 제55항 | `81` | ⠦⠂ (2-3-6 · 2) | ⠦⠂ | 예 |
| 닫는 중괄호 `}` | 제55항 | `"0` | ⠐⠴ (5 · 3-5-6) | ⠐⠴ | 예 |
| 여는 대괄호 `[` | 제56항 | `82` | ⠦⠆ (2-3-6 · 2-3) | ⠦⠆ | 예 |
| 닫는 대괄호 `]` | 제56항 | `;0` | ⠰⠴ (5-6 · 3-5-6) | ⠰⠴ | 예 |
| 로마자 표 | 제30항 | `0` | ⠴ (3-5-6) | ⠴ | 예 |
| 로마자 종료표 | 제30항 | `4` | ⠲ (2-5-6) | ⠲ | 예 |

미구현 부호(가운뎃점·빗금·따옴표·낫표·줄표·물결표·별표·긴소리표·화폐 기호)는
`notes/2026-08-13-regulation-audit.md`에 정리해 두었다.

제54항 해설이 개정 사유를 밝히고 있다.

> 소괄호 점형은 이번 『개정 한국 점자 규정』(2017)에서 많은 논의 끝에 개정되었다.
> 이는 ⠤이 소괄호, 붙임표, 줄표 등에서 다양하게 사용되어 여러 예외 규정이 생기는 등
> 혼동을 일으켜 왔고, 소·중·대괄호의 점형을 모두 중·하단 점형 두 칸으로 통일하여
> 표기함으로써 일관성을 유지하기 위함이다.

인코더가 쓰던 단일 ⠤ 표기는 **개정 전 형태**로, 2017 개정이 없앤 바로 그
혼동(괄호·붙임표 구분 불가)을 그대로 재현하고 있었다. 2026-08-13에 두 칸 표기로
옮겼다.

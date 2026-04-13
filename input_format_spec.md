# 1단계(v1): 영어 점자 해석 파이프라인 스펙

## 1. 목표

본 단계(v1)의 목표는 다음과 같다.

> 영어 UEB 점자 파일을 입력으로 받아,
> (1) 영어 평문 텍스트,
> (2) 문단·리스트·표·수식 등 기본 구조 정보,
> (3) 선택적으로 한국어 요약 텍스트
> 를 자동으로 생성하는 시스템을 구축한다.

이 단계에서는 **점자를 새로 생성하는 기능은 포함하지 않고**, 점자에 인코딩된 내용을 사람이 읽고 활용하기 좋은 형태로 복원·구조화하는 데 집중한다.

---

## 2. 입력 점자 파일 포맷 가정

v1에서는 영어 점자 입력을 다음과 같이 가정한다.

- 형식: 텍스트 기반 점자 파일 (예: BRF)
- 인코딩: UTF-8
- 단위:
  - 한 줄(line)은 점자 셀 한 줄에 대응한다.
  - 줄 길이는 대략 32-40셀 이내로 가정한다.
- 페이지 구분:
  - `=== PAGE BREAK ===` 와 같은 특수 문자열 한 줄로 페이지 경계를 표현한다.
- 문단 구분:
  - 빈 줄(공백 문자만 있는 줄) 한 줄 이상을 문단 경계로 간주한다.

예시 (실제 점자 기호 대신 "점자 문자열"로 표기):

```text
⠠⠞⠓⠊⠎ ⠊⠎ ⠁ ⠎⠊⠍⠏⠇⠑ ⠎⠑⠝⠞⠑⠝⠉⠑⠲
⠠⠊⠞ ⠊⠎ ⠥⠎⠑⠙ ⠊⠝ ⠁ ⠃⠗⠁⠊⠇⠇⠑ ⠃⠕⠕⠅⠲

⠠⠞⠓⠑ ⠧⠁⠇⠥⠑ ⠕⠋ ⠭ ⠊⠎ ⠁⠏⠏⠗⠕⠭⠊⠍⠁⠞⠑⠇⠽ ⠼⠉⠲⠁⠙⠲
=== PAGE BREAK ===
⠁⠝⠕⠞⠓⠑⠗ ⠏⠁⠗⠁⠛⠗⠁⠏⠓ ⠋⠕⠇⠇⠕⠺⠎⠲
```

위와 같은 구조를 가진 텍스트 파일을 v1에서의 대표 입력으로 삼는다.

---

## 3. 중간 결과 데이터 구조

### 3.1 점자 → 영어 텍스트

점자 역점역과 노이즈 보정을 위한 인터페이스는 다음 두 단계로 나눈다.

- 역점역:
  - 함수 개념: `braille_to_text(braille_str, lang="en") -> rough_text`
  - 역할: 점자 문자열을 영어 텍스트로 변환하되, 오타·구두점 누락 등 노이즈가 포함될 수 있다.
- 노이즈 보정:
  - 함수 개념: `correct_noisy_text(rough_text, lang="en") -> corrected_text`
  - 역할: 역점역 과정에서 발생한 노이즈를 LLM 등으로 문맥 기반 보정한다.

이를 하나의 JSON으로 표현하면 다음과 같은 형태를 갖는다.

```json
{
  "doc_id": "sample_001",
  "english_text": {
    "rough": "Ths is a smple sentence. It is used in a braille book.",
    "corrected": "This is a simple sentence. It is used in a braille book."
  }
}
```

여기서 `rough`는 점자 엔진의 원출력, `corrected`는 노이즈 보정 이후 결과를 의미한다.

### 3.2 구조 정보(문단·리스트·표·수식)

점자 파일의 줄 패턴을 분석하여 최소한의 문서 구조를 추출하고, 다음과 같은 블록 리스트로 표현한다.

블록 타입:

- `"P"`: Paragraph (문단)
- `"L"`: List (리스트)
- `"T"`: Table (표)
- `"M"`: Math (수식)

JSON 예시:

```json
{
  "doc_id": "sample_001",
  "structure": {
    "blocks": [
      {
        "block_id": "b1",
        "type": "P",
        "start_line": 1,
        "end_line": 2
      },
      {
        "block_id": "b2",
        "type": "P",
        "start_line": 4,
        "end_line": 4
      },
      {
        "block_id": "b3",
        "type": "M",
        "start_line": 6,
        "end_line": 7
      }
    ]
  }
}
```

- `start_line`, `end_line`은 점자 파일 내 줄 번호(1부터 시작)를 나타낸다.
- 리스트, 표, 수식에 대해서도 동일한 방식으로 블록을 정의한다.

이 구조 정보는 이후 번역·요약 단계에서 "어떤 부분이 문단/리스트/표/수식인지"를 보존하는 데 사용된다.

---

## 4. 최종 출력 포맷 (v1)

1단계에서 목표로 하는 "점자 해석 결과"를 하나의 JSON으로 종합하면 다음과 같이 정의할 수 있다.

```json
{
  "doc_id": "sample_001",
  "source_braille_path": "data/braille/en/sample_001.brf",

  "english_text": {
    "rough": "Ths is a smple sentence. It is used in a braille book.",
    "corrected": "This is a simple sentence. It is used in a braille book."
  },

  "structure": {
    "blocks": [
      { "block_id": "b1", "type": "P", "start_line": 1, "end_line": 2 },
      { "block_id": "b2", "type": "P", "start_line": 4, "end_line": 4 },
      { "block_id": "b3", "type": "M", "start_line": 6, "end_line": 7 }
    ]
  },

  "korean_summary": {
    "text": "이 문서는 점자 책의 간단한 예시 문장을 설명한다.",
    "num_sentences": 1
  }
}
```

- v1에서 **필수 출력**: `english_text.corrected` + `structure.blocks`
- **선택 출력**: `korean_summary` (구현 여건에 따라 추가/생략)

---

## 5. 파이프라인 처리 흐름

```
입력: 영어 점자 파일 (UEB, 텍스트 기반)
  │
  ├─ 1) load_braille(path)           → raw_lines, pages, metadata
  │
  ├─ 2) braille_to_text(str)         → rough_text (노이즈 포함)
  │
  ├─ 3) correct_noisy_text(str)      → corrected_text (보정 완료)
  │
  ├─ 4) extract_structure(lines)     → blocks [{type, start_line, end_line}]
  │
  └─ 5) assemble_output(...)         → 최종 JSON (위 포맷)
```

---

## 6. 함수 인터페이스 요약

```python
# 파일 로드
load_braille(file_path: str) -> dict

# 역점역
braille_to_text(braille_str: str, lang: str = "en") -> str

# 노이즈 보정
correct_noisy_text(noisy_text: str, lang: str = "en") -> str

# 구조 추출
extract_structure(lines: list[str]) -> list[dict]

# 출력 조합
assemble_output(doc_id, source_path, rough, corrected, blocks,
                korean_summary=None) -> dict
```

---

## 7. v1 범위 밖

- 한국어 점자 생성 (Phase 2)
- 점자 이미지/embosser 파일 처리
- BRF 이외의 점자 포맷 (PEF 등)
- 점자 음악/이미지 설명
- 외국어 삽입, 컴퓨터 점자(CBC)
- Nemeth 수학 점자 (고급 수식)

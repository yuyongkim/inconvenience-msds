# 2026-04-15 KR 디코더 수정 계획

## 목표
한국어 점자 경로의 신뢰성을 회복하기 위해 아래 4가지를 우선 해결합니다.

1. 한국어 decode entrypoint를 올바르게 연결
2. `ko_braille_decoder.py`의 핵심 오해석 로직 수정
3. KR 평가를 EN/번역 평가와 분리
4. 회귀 테스트를 추가해 재발을 방지

---

## 1단계. 중앙 decode entrypoint 수정

### 대상 파일
- `pipeline/decoder.py`

### 현재 문제
- `braille_to_text(..., lang='ko')`가 실제로 한국어 전용 decoder로 분기하지 않습니다.
- 이 때문에 KR 테스트도 사실상 일반 decoder를 타고 있습니다.

### 수정 방향
- `lang == 'ko'`이면 `pipeline.ko_braille_decoder.decode_korean_braille()` 호출
- 그 외만 기존 `decode_unicode_braille()` / BRF 경로 유지

### 기대 효과
- 테스트와 실제 호출 경로가 일치합니다.
- KR 품질 수치가 최소한 “한국어 decoder”를 반영하게 됩니다.

---

## 2단계. `ko_braille_decoder.py` 구조 개편

### 대상 파일
- `pipeline/ko_braille_decoder.py`

### 현재 문제 요약
1. punctuation를 종성으로 먼저 먹는 문제
2. 멀티셀 초성/중성/종성을 longest-match 하지 못하는 문제
3. punctuation reverse mapping이 비가역적인 문제
4. Latin/숫자 모드가 비대칭적인 문제

### 수정 우선순위

#### 2-1. longest-match 매칭 도입
- 초성/중성/종성 모두 1셀 가정 제거
- 가능한 후보 중 가장 긴 매칭을 우선 적용
- 멀티셀 자모를 정식 지원

#### 2-2. punctuation vs 종성 문맥 분기 추가
우선 처리해야 할 대표 충돌:
- `.` vs `ㅍ`
- `,` vs `ㄹ`
- `?` / `"` vs `ㅌ`
- `;` vs `ㅊ`

규칙 방향:
- 음절 종료 후 문자열 끝 / 공백 / 다른 punctuation이면 punctuation 우선
- 다음에 모음이 이어지거나 음절 내부이면 종성 우선

#### 2-3. Latin / 숫자 모드 복구
- Roman indicator 해석
- capital indicator 해석
- number mode 종료/유지 규칙 명확화

#### 2-4. punctuation 처리 방식을 단일 reverse dict에서 분리
- 충돌 셀을 단순 `dict` reverse map으로 처리하지 않음
- 문맥 기반 해석 함수로 분리

### 구현 방식 제안
- state machine 기반으로 재작성
- 최소 상태:
  - base
  - in_number
  - in_latin
  - reading_hangul_syllable

---

## 3단계. 테스트 구조 분리

### 대상 파일
- 기존: `tests/test_braille_roundtrip.py`
- 신규 분리 권장:
  - `tests/test_ko_encoder_golden.py`
  - `tests/test_ko_decoder_golden.py`
  - `tests/test_ko_roundtrip.py`
  - `tests/test_en_roundtrip.py`

### 목적 분리

#### 3-1. KO encoder test
- 입력: KO text
- 출력: gold KO braille
- decoder 사용 금지
- 측정: braille exact match / braille edit similarity / rule violation

#### 3-2. KO decoder test
- 입력: gold KO braille
- 출력: expected KO text
- 측정: text-level similarity
- 오류 bucket 분류 포함

#### 3-3. KO round-trip test
- 입력: KO text
- 경로: encode -> decode
- 목적: 조합 안정성 확인
- 주의: encoder 품질 지표로 사용 금지

#### 3-4. EN round-trip test
- 기존 EN 테스트는 별도로 유지

### 추가 원칙
- 내부 계산은 raw float 유지
- 출력/CSV 저장 시에만 반올림

---

## 4단계. misleading 평가 제거 또는 이름 변경

### 대상 파일
- `tests/test_e2e_golden.py`
- `eval/run_e2e_eval.py`

### 현재 문제
- KR-native 평가처럼 보이지만 실제로는 EN decode + translation + fallback + KO encode가 섞여 있습니다.
- `eval/run_e2e_eval.py`는 stub/no-op fallback이 있어 신뢰할 수 없습니다.

### 수정 방향

#### 4-1. `tests/test_e2e_golden.py`
- KR 품질 지표에서 제외
- 이름 변경 권장:
  - `test_en_pipeline_to_ko_translation_smoke.py`

#### 4-2. `eval/run_e2e_eval.py`
- 실제 한국어 decoder import 실패 시 즉시 실패
- braille text 그대로 반환하는 fallback 제거

#### 4-3. translation 평가 분리
신규 파일 예시:
- `eval/eval_translation_en_ko.py`
- `eval/eval_ko_encoder.py`
- `eval/eval_ko_decoder.py`

---

## 5단계. 회귀 테스트 문장 고정

반드시 고정할 케이스:

### punctuation 충돌
- `이것은 간단한 문장입니다.`
- `정말 확실해?`
- `소위 "모범 사례"가 항상 최선은 아니다.`

### 쌍자음 / 복모음
- `오늘 날씨가 참 좋습니다.`
- `소위`
- `중합효소 연쇄 반응`

### 숫자 / 기호
- `자세한 내용은 02-555-1234로 전화해 주세요.`
- `회의는 2026년 4월 6일 오후 3시 45분에 시작합니다.`

### Latin 혼합
- `HTTP 상태 코드 404`
- `NaCl`
- `CPU`
- `A36`
- `f(x) = 2x + 1`

---

## 추천 실행 순서

### 이번 작업 사이클
1. `pipeline/decoder.py` 한국어 분기 연결
2. `pipeline/ko_braille_decoder.py` punctuation/멀티셀 우선 수정
3. KR decoder golden test 추가
4. KR round-trip test 분리
5. `tests/test_e2e_golden.py` 역할 축소 또는 이름 변경
6. `eval/run_e2e_eval.py` fallback 제거

### 그 다음 사이클
1. Latin/숫자 모드 정교화
2. ambiguity bucket 리포트 추가
3. README / paper의 평가 문구 업데이트

---

## 최종 판단
이 프로젝트의 핵심 기능은 여전히 **한글 MSDS -> 점자 생성**입니다.
하지만 그 기능의 신뢰성을 지지해야 할 **디코더 / round-trip / 평가 구조**가 현재 약합니다.
따라서 다음 실제 구현 작업은 **디코더 우선**이 맞습니다.

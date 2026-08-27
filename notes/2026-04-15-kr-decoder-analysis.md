# 2026-04-15 KR 디코더 및 평가 구조 분석

## 요약
현재 KR 품질 저점수는 단순히 "한국어 MSDS -> 점자 인코더가 실패했다"는 뜻으로 해석하면 안 됩니다.
다만 반대로, 현재 상태가 안전하다고 보기도 어렵습니다.

정확한 판단은 아래와 같습니다.

- 한국어 인코더 경로 자체는 프로젝트의 중심 기능으로 유지될 가능성이 높습니다.
- 그러나 한국어 디코더와 KR 평가 경로가 현재 왜곡되어 있습니다.
- 따라서 중심 기능의 신뢰성을 주장하려면 **디코더와 평가 구조를 먼저 바로잡아야 합니다.**

---

## 1. 확인된 핵심 문제

### 1-1. KR round-trip 테스트가 잘못된 디코더를 사용 중
파일:
- `tests/test_braille_roundtrip.py`
- `pipeline/decoder.py`

문제:
- KR 인코딩은 `encode_korean_braille()`를 사용합니다.
- 그러나 decode는 `pipeline.decoder.braille_to_text()`를 그대로 사용합니다.
- `braille_to_text(..., lang='ko')`는 실제 한국어 전용 분기를 하지 않습니다.
- 따라서 현재 `--lang ko` 결과는 한국어 전용 decoder 품질을 올바르게 반영하지 않습니다.

의미:
- 현재 KR 저점수는 평가 경로 자체가 잘못 연결된 결과가 섞여 있습니다.

---

### 1-2. 한국어 전용 디코더 자체도 완전하지 않음
파일:
- `pipeline/ko_braille_decoder.py`

직접 확인 예시:
- 원문: `이것은 간단한 문장입니다.`
- decode 결과: `이것은 간단한 문장입니닾`

대략 확인된 평균:
- golden 45문장 기준 `avg_edit ≈ 0.7675`
- `avg_chrf ≈ 0.6595`

즉:
- 기존 테스트 수치는 과장되게 나빴지만,
- 올바른 한국어 디코더를 써도 실제 문제는 남아 있습니다.

---

## 2. 디코더의 구체적 실패 원인

### 2-1. 문장 끝 punctuation를 종성으로 먼저 먹는 문제
문제 위치:
- `pipeline/ko_braille_decoder.py`

예시:
- `입니다.` -> `입니닾`

원인:
- period에 해당하는 점자 셀이 종성 `ㅍ`과 충돌합니다.
- 디코더가 punctuation보다 종성 해석을 먼저 해버립니다.

비슷한 충돌 후보:
- `ㅅ` / apostrophe
- `ㅌ` / `?` / `"`
- `ㅊ` / `;`
- `ㄹ` / `,`

---

### 2-2. 멀티셀 자모를 제대로 longest-match 하지 못함
문제 위치:
- encoder: `pipeline/ko_braille.py`
- decoder: `pipeline/ko_braille_decoder.py`

문제:
- encoder는 쌍자음, 복모음, 일부 겹받침을 멀티셀로 생성합니다.
- decoder는 이를 충분히 longest-match 하지 못합니다.

대표 사례:
- `날씨` 계열
- `소위`, `중합효소` 같은 복모음 포함 단어

---

### 2-3. punctuation 매핑이 비가역적임
문제 위치:
- `pipeline/ko_braille.py`
- `pipeline/ko_braille_decoder.py`

문제:
- 서로 다른 문장부호가 동일 점자 셀로 encode됩니다.
- reverse map을 단일 dict로 만들면서 마지막 값만 남습니다.

예시:
- `-`, `(`, `)`가 같은 셀
- `?`, `"`가 같은 셀
- 그 결과 `02-555-1234`가 `02)555)1234`처럼 복원될 수 있습니다.

---

### 2-4. Latin/숫자 혼합 모드가 비대칭
문제 위치:
- `pipeline/ko_braille.py`
- `pipeline/ko_braille_decoder.py`

문제:
- encoder는 Roman indicator, capital indicator를 넣습니다.
- decoder는 이를 충분히 대칭적으로 해석하지 못합니다.

영향 사례:
- `HTTP`
- `CPU`
- `NaCl`
- `A36`
- `f(x)`

---

## 3. 평가 구조 자체의 왜곡

### 3-1. `tests/test_e2e_golden.py`는 KR-native 품질 테스트가 아님
이 테스트는 사실상:
- EN text -> EN braille -> decode -> correct -> translate EN->KO -> KO braille
경로를 검증합니다.

즉:
- 한국어 원문 MSDS -> 한국어 점자 품질 테스트가 아닙니다.
- EN decode / translation / network 상태 / KO encode가 섞입니다.

따라서 이 결과를 KR braille 품질로 읽으면 안 됩니다.

---

### 3-2. `eval/run_e2e_eval.py`는 stub fallback 때문에 신뢰하기 어려움
문제:
- 실제 한국어 디코더를 쓰지 못하면 braille text를 그대로 반환하는 fallback이 존재합니다.
- 이 경우 의미 없는 수치가 조용히 계산될 수 있습니다.

즉:
- import 실패 시 즉시 실패하도록 바꿔야 합니다.

---

## 4. 최우선 수정 순서

### 1순위
`pipeline/decoder.py`의 `braille_to_text()`에 한국어 분기를 실제로 연결
- `lang == 'ko'`이면 `decode_korean_braille()` 호출

### 2순위
`pipeline/ko_braille_decoder.py` 재작성 또는 대폭 보강
핵심 방향:
- longest-match state machine
- 초성/중성/종성 멀티셀 처리
- punctuation vs 종성 문맥 분기
- Latin / 숫자 모드 대칭 처리

### 3순위
KR 테스트 분리
권장 분리:
- `test_ko_encoder_golden.py`
- `test_ko_decoder_golden.py`
- `test_ko_roundtrip.py`

### 4순위
`tests/test_e2e_golden.py`를 KR 품질 지표에서 제외 또는 이름 변경
예:
- `test_en_pipeline_to_ko_translation_smoke.py`

### 5순위
`eval/run_e2e_eval.py`에서 stub/no-op fallback 제거
- decoder import 실패 시 즉시 실패

### 6순위
translation 평가와 braille 평가 분리
- translation benchmark
- KO encoder benchmark
- KO decoder benchmark
- KO round-trip benchmark

---

## 5. 최종 결론
지금 KR 저점수는 아래 두 가지가 동시에 맞습니다.

1. **평가가 잘못 연결되어 있어서 수치를 그대로 믿으면 안 됩니다.**
2. **그렇다고 문제가 없는 것도 아니며, 한국어 디코더는 실제로 중심부 품질 이슈입니다.**

즉 가장 정직한 표현은 다음과 같습니다.

> 현재 프로젝트의 핵심 경로인 "한글 MSDS -> 점자 생성" 자체가 즉시 무효라고 단정할 근거는 부족합니다.
> 그러나 그것을 검증하고 뒷받침하는 KR decoder / round-trip / evaluation layer는 현재 신뢰성이 부족하며,
> 이 부분은 프로젝트 중심 기능의 핵심 리스크로 다루어야 합니다.

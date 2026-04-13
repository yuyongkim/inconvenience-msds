# Braille LLM Pipeline – Evaluation & Harness Spec

이 문서는 **영어 점자 → 한국어 점자 번역 파이프라인**을 평가하기 위한 데이터셋 설계와 실험 하네스(테스트/평가 틀)를 정의한다.  
파이프라인 구현은 LLM(예: Claude)을 활용해 진행하되, 이 문서에 정의된 형식과 지표를 만족하도록 코드를 작성한다.

구성은 세 부분으로 나뉜다.

1. A: BrailleIO 라운드트립(텍스트↔점자) 골든셋  
2. B: LLM 노이즈 보정(Noise Correction) 평가 하네스  
3. C: 엔드투엔드(점자→점자) 평가 지표 및 포맷

---

## A. BrailleIO Round-trip Golden Set

### A.1 목적

- 텍스트 → 점자 → 텍스트 round-trip이 규정에 맞게 동작하는지 검증하는 **언어별(EN/KR) 골든셋** 정의.
- 라이브러리/테이블/규칙이 바뀌어도, 이 골든셋으로 회귀 테스트를 돌려서 품질 변화를 추적한다.

### A.2 데이터 파일 포맷

언어별로 각각 하나의 CSV 파일을 사용한다.

- 영어: `golden_braille_roundtrip_en.csv`  
- 한국어: `golden_braille_roundtrip_ko.csv`

공통 컬럼:

- `id` : 고유 ID (예: `en_001`, `ko_001`)
- `source_text` : 깨끗한 평문 (점자 변환의 기준)
- `category` : 예문 유형 태그

`category` 값 예시:

- `basic` : 기본 문장 구조 (평서, 의문 등)
- `number` : 숫자/날짜/시간/단위 포함
- `list` : 리스트/열거 표현
- `quote` : 괄호/인용부호/대시 등
- `math` : 간단 수식/수학 표현
- `domain` : 화학/공학/CS 등 도메인 용어 포함

예시 (영어):

```csv
id,source_text,category
en_001,"This is a simple sentence.",basic
en_007,"The meeting starts at 3:45 p.m. on April 6, 2026.",number
en_012,"The temperature ranges from 20°C to 25°C in the reactor.",domain
en_021,"If x^2 = 4, then x is either 2 or -2.",math
```

예시 (한국어):

```csv
id,source_text,category
ko_001,"이것은 간단한 문장입니다.",basic
ko_007,"회의는 2026년 4월 6일 오후 3시 45분에 시작합니다.",number
ko_015,"반응기 온도는 20도에서 25도 사이를 유지해야 합니다.",domain
ko_023,"만약 x 제곱이 4라면, x는 2 또는 마이너스 2입니다.",math
```

### A.3 테스트 하네스 요구사항

테스트 스크립트(예: `tests/test_braille_roundtrip.py`)는 다음을 수행해야 한다.

1. CSV 파일 읽기  
2. 각 행에 대해:
   - `source_text` → `encode_braille` → 점자 문자열
   - 점자 문자열 → `decode_braille` → `roundtrip_text`
3. `source_text` vs `roundtrip_text` 간 유사도 계산:
   - 공백/구두점 제외 여부 옵션 지원
   - 간단한 문자/토큰 기반 유사도 지표 사용 (예: 1 - edit_distance / max_len)
4. 문장별 점수 및 `category`별 평균 점수 출력

출력 예(콘솔 또는 별도 CSV):

```csv
id,category,source_text,roundtrip_text,sim_score
en_001,basic,"This is a simple sentence.","This is a simple sentence.",0.98
...
```

---

## B. LLM Noise Correction Evaluation

### B.1 목적

- 역점역(점자→텍스트) 단계에서 발생하는 노이즈를 LLM(NoiseCorrector)이 실제로 줄여주는지 정량적으로 평가한다.
- 노이즈 유형별로 보정 효과를 비교할 수 있게 한다.

### B.2 노이즈 타입 카테고리

다음 7가지 노이즈 타입을 사용한다.

1. `missing_punctuation`  
   - 마침표, 콤마, 물음표, 따옴표 등이 빠진 경우

2. `merged_words`  
   - 단어 사이 공백이 사라져 한 단어처럼 붙은 경우

3. `split_words`  
   - 한 단어가 둘로 나뉜 경우

4. `spelling_variation`  
   - 철자 오류, 비표준 철자

5. `dropped_function_words`  
   - 관사·전치사·조동사 등 기능어가 빠진 경우

6. `number_format_noise`  
   - 숫자·소수점·기호(%, °C 등)가 깨진 경우

7. `mixed_noise`  
   - 위 유형이 두 개 이상 섞인 경우

### B.3 데이터 파일 포맷

파일 이름: `noise_correction_eval_en.csv`

컬럼:

- `id` : 고유 ID (예: `nc_001`)
- `clean_en` : 원본 깨끗한 영어 문장
- `noisy_en` : 노이즈가 포함된 영어 문장
- `noise_type` : 위 7개 타입 중 하나
- `corrected_en` : LLM 보정 결과 (초기에는 빈 값, 코드가 채움)

예시:

```csv
id,clean_en,noisy_en,noise_type,corrected_en
nc_001,"This is a simple sentence.","This is a simple sentence",missing_punctuation,
nc_002,"The value of x is approximately 3.14.","The value of x is aproximatly 3 14",spelling_variation,
nc_003,"We used a neural network model in this experiment.","We used a neuralnetwork model in this experiment.",merged_words,
nc_004,"The reactor temperature is 20°C under normal conditions.","The reactor temprature is 20C under normal conditions.",spelling_variation,
nc_005,"In Figure 3, the conversion rate increases from 20% to 35%.","In figure3 the conversion rate increase from 20 to 35",mixed_noise,
```

### B.4 평가 스크립트 요구사항

평가 스크립트(예: `eval/run_noise_correction_eval.py`)는 다음을 수행해야 한다.

1. `noise_correction_eval_en.csv` 읽기  
2. `corrected_en`이 비어 있는 행에 대해:
   - LLM NoiseCorrector를 호출해 보정 결과를 생성하고 `corrected_en` 채우기
3. 각 행에 대해:
   - `sim_clean_noisy` = sim(`clean_en`, `noisy_en`)
   - `sim_clean_corrected` = sim(`clean_en`, `corrected_en`)
   - `delta_sim` = `sim_clean_corrected - sim_clean_noisy`
4. 결과를 별도 CSV로 저장: `noise_correction_results.csv`

출력 CSV 예:

```csv
id,noise_type,sim_clean_noisy,sim_clean_corrected,delta_sim
nc_001,missing_punctuation,0.92,0.99,0.07
nc_002,spelling_variation,0.80,0.95,0.15
...
```

5. 추가 통계:
   - 전체 평균 `delta_sim`
   - `delta_sim > 0` 비율
   - `noise_type`별 평균/표준편차

---

## C. End-to-End Braille-to-Braille Evaluation

### C.1 목적

- 전체 파이프라인 (영어 점자 → 한국어 점자)의 품질을 Baseline과 Proposed 시스템 간에 비교한다.
- **텍스트 의미**, **문서 구조**, **점자 규정/형태** 세 축으로 평가한다.

### C.2 평가 단위와 데이터

평가 단위: 문서/섹션 단위 (예: 1-2 페이지 수준)

각 문서에 대해 다음 정보를 전제한다.

- `doc_id` : 문서 ID (예: `d01`)  
- `src_braille_en_path` : 영어 점자 입력 파일  
- `gold_ko_text` : 가능하면, 점역사가 만든 한국어 텍스트 골든셋 (없으면 일부 문단만이라도)

각 시스템 출력:

- Baseline: 기존 파이프라인 결과 한국어 점자
- Proposed: 본 논문 시스템 결과 한국어 점자

이 두 결과는 별도 디렉터리에 파일로 저장해두고, 평가 스크립트가 불러다 쓴다.

### C.3 핵심 지표 3개

#### 1) 텍스트 의미 품질 – `text_sim_score`

설명:

- 각 시스템의 한국어 점자 결과를 다시 한국어 텍스트로 풀어낸 뒤,
- `gold_ko_text`와의 유사도를 계산하는 지표.
- 구체 지표는 chrF 또는 간단한 문자열 유사도(1 - edit_distance / max_len)로 구현.

문서별로:

- `text_sim_score_baseline`
- `text_sim_score_proposed`

#### 2) 문서 구조 보존 – `structure_f1`

설명:

- 문서 구조를 추상화:
  - 문단(Paragraph), 리스트(List), 표(Table), 수식(Math) 블록 수/순서
- 골든 구조와 시스템 구조를 비교해 "블록 단위 탐지 문제"로 본다.
- 블록이 골든과 타입·순서 면에서 얼마나 일치하는지 precision/recall/F1로 측정.

간단한 구현 아이디어:

- 각 문서를 `{para_count, list_count, table_count, math_count}` 벡터로 표현
- 각 항목에 대해 시스템과 골든의 min/max 기반 "일치도"를 계산한 뒤 종합 F-score로 환산  
  (추후 필요 시 더 정교한 블록 매칭으로 확장 가능)

문서별로:

- `structure_f1_baseline`
- `structure_f1_proposed`

#### 3) 점자 규정/형태 오류율 – `rule_violation_rate`

설명:

- 한국어 점자 규정/관행 중 자동 체크 가능한 몇 가지 규칙만 골라,
- "규칙 위반 개수 / 1,000 점자 셀"로 정규화한 값.

후보 규칙 예:

- 숫자 표기 규칙:
  - 숫자 앞 점자 기호(숫자 표지) 누락/오용
- 괄호/따옴표 짝:
  - 열린 괄호/따옴표가 닫히지 않거나 순서가 뒤틀린 경우
- 특정 약자 사용:
  - 규정상 약자를 써야 하는 패턴에서 전부 풀어 쓴 경우 등 (간단 버전만)

문서별로:

- `rule_violation_rate_baseline`
- `rule_violation_rate_proposed`

### C.4 결과 파일 포맷

엔드투엔드 평가 결과는 CSV로 저장한다. 파일 이름: `e2e_eval_results.csv`

컬럼:

- `doc_id`
- `text_sim_score_baseline`
- `text_sim_score_proposed`
- `structure_f1_baseline`
- `structure_f1_proposed`
- `rule_violation_rate_baseline`
- `rule_violation_rate_proposed`

예:

```csv
doc_id,text_sim_score_baseline,text_sim_score_proposed,structure_f1_baseline,structure_f1_proposed,rule_violation_rate_baseline,rule_violation_rate_proposed
d01,0.62,0.78,0.55,0.81,7.3,3.1
d02,0.58,0.71,0.49,0.76,8.5,4.0
...
```

평가 스크립트(예: `eval/run_e2e_eval.py`)는 다음을 수행해야 한다.

1. 문서 목록(입력 점자/골든 텍스트/시스템 출력 경로)을 읽는다.  
2. 각 문서에 대해:
   - Baseline/Proposed 출력에 대해 3개 지표 계산  
3. 위 CSV 형식을 채워 작성한다.  
4. 전체 평균/표준편차, paired test 등 후처리는 별도 노트북/스크립트에서 수행.

---

## D. Data Sources & Construction Plan

데이터는 **"당장 쓸 수 있는 것"**과 **"협의/구축이 필요한 것"**으로 나눠 기획한다.

### D.1 A용 – 라운드트립 골든셋

| 항목 | 전략 | 비고 |
|------|------|------|
| 영어 예문 | **자체 작성** (카테고리별 20-50문장) | 공개 코퍼스(WMT, Wikipedia)는 패턴 참고용 |
| 한국어 예문 | **자체 작성** (카테고리별 20-50문장) | 국립국어원 공공 예문은 참고용 |
| 점자 데이터 | 엔진이 생성 (외부 점자 코퍼스 불필요) | encode→decode로 자동 생성 |

핵심: 외부 대형 데이터셋 불필요. 연구자가 직접 설계하는 작은 고급 골든셋이 적합.

### D.2 B용 – 노이즈 보정 실험

#### clean 문장 소스

1. A 골든셋의 영어 문장 **재사용**
2. 추가 도메인 문장: 공개 논문/교재 내용을 참고해 **연구자가 재작성** (저작권 부담 최소화)

#### noisy 문장 생성 전략 (2단계)

| 단계 | 방법 | 시점 |
|------|------|------|
| 초기 | **인공 노이즈 규칙**으로 생성 (스크립트) | 지금 바로 가능 |
| 후기 | 실제 역점역(점자→텍스트) 결과를 병행 | 엔진 안정화 후 |

인공 노이즈 규칙 예:

- `missing_punctuation`: 마침표/콤마/물음표를 랜덤 제거
- `merged_words`: 인접 단어 쌍의 공백을 제거
- `split_words`: 단어 중간에 공백 삽입
- `spelling_variation`: 자음/모음 1글자 치환/삭제
- `dropped_function_words`: a/the/is/of/to 등 랜덤 제거
- `number_format_noise`: 소수점 제거, 단위기호(%, °C) 제거/변형
- `mixed_noise`: 위 규칙 2개 이상 동시 적용

### D.3 C용 – 엔드투엔드 평가

#### 초기 전략 (외부 협약 없이 가능)

```
영어 평문 (공개 텍스트)
  → 영어 점자 (우리 엔진으로 생성) ← 입력
  → 한국어 텍스트 (기계번역 + 수동 수정) ← 골든 텍스트
  → 한국어 점자 (엔진 + 수동 검수) ← 골든 점자
```

- 규모: 문서 5-10개, 각 1-2페이지 분량
- 영어 텍스트 소스: 오픈액세스 논문, CC 라이선스 교재, Wikipedia
- 한국어 골든: 기계번역 초안 → 연구자 수동 교정

#### 장기 확장 전략 (협약 기반)

- 시각장애인 도서관/점자도서관/학교와 **연구 협약** 체결
- 실제 사용 중인 영어 점자 교재 일부 + 공식 한국어 번역
- 또는 시각장애인 대학생의 실제 학습 자료 일부를 연구용으로 제공

### D.4 사용자 연구용 (추후)

- 대상: 시각장애인 대학생/연구자 5-10명
- 데이터: Baseline vs Proposed 두 버전 변환 샘플
- 수집: 읽기 편의성, 치명적 오류 유형 피드백
- 요건: 기관 IRB/윤리 심사 필요
- 현 단계에서는 계획만 수립, A/B/C 자동 평가에 집중

### D.5 요약 테이블

| 평가 | 데이터 | 소스 전략 | 즉시 가능 여부 |
|------|--------|-----------|---------------|
| A 라운드트립 | EN/KR 예문 30-50문장씩 | 자체 작성 | **즉시** |
| B 노이즈 | clean+noisy 문장 쌍 | A 재사용 + 인공 노이즈 | **즉시** |
| C E2E 입력 | 영어 점자 문서 5-10개 | 공개 텍스트 → 자체 점역 | **즉시** |
| C E2E 골든 | 한국어 텍스트+점자 | 기계번역 + 수동 교정 | **즉시** (소규모) |
| C E2E 확장 | 실제 교재 점자판 | 기관 협약 필요 | 중장기 |
| 사용자 연구 | 피드백 로그 | IRB + 참여자 모집 | 중장기 |

---

## TODO 체크리스트 (요약)

- [ ] `golden_braille_roundtrip_en.csv` / `ko.csv` 문장 채우기  
- [ ] `noise_correction_eval_en.csv` clean/noisy 샘플 채우기  
- [ ] BrailleIO round-trip 테스트 스크립트 구현  
- [ ] NoiseCorrection 평가 스크립트 구현 (`noise_correction_results.csv` 생성)  
- [ ] 엔드투엔드 평가 스크립트 구현 (`e2e_eval_results.csv` 생성)  
- [ ] 점자 규정 기반 rule check 함수(3-5개 규칙) 정의  

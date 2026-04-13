# Phase 1 Roadmap – 점자 해석 (Braille → Text/Structure/Understanding)

## 목표 (v1)

영어 점자 파일(UEB 기준)을 입력으로 받아서:
1. 영어 평문 텍스트
2. 기본 구조 정보 (문단/리스트/표/수식 위치)
3. (선택) 한국어 요약 텍스트

까지 뽑아내는 시스템.

**이 단계에서는 점자를 생성하지 않는다.**
오로지 "점자가 뭘 의미하는지, 어떤 구조인지 뽑아내는 것"에 집중.

---

## 최소 엔드투엔드 파이프라인

```
입력: 영어 점자 파일 (UEB, 텍스트 기반, BRF 형식)
  │
  ├─ 1) 점자 문자열 로드 (load_brf)
  │
  ├─ 2) 역점역 (braille_to_text)
  │     rough 영어 텍스트 생성
  │
  ├─ 3) 노이즈 보정 (correct_noisy_text)
  │     LLM 기반 텍스트 정제
  │
  ├─ 4) 구조 추출 (extract_structure)
  │     점자 줄 패턴 → P/L/T/M 블록
  │
  └─ 5) 출력 조합 (assemble_output)
        영어 평문 + 구조 → Markdown
        (옵션) 영어→한국어 요약
```

---

## 구현 순서

1. 입력 포맷 스펙 고정 → `input_format_spec.md`
2. 인터페이스 + JSON 예시 고정 → `pipeline/interfaces.py`
3. 골든셋/테스트로 역점역 품질 기준선 확보 (A 평가)
4. 노이즈 보정 모듈 연결 + B 평가
5. 구조 추출 휴리스틱 구현
6. 전체 파이프라인 연결 + 수동 검증

---

## 범위 밖 (v1에서 안 함)

- 한국어 점자 생성 (Phase 2)
- 점자 이미지/embosser 파일 처리
- BRF 이외의 점자 포맷 (PEF, BRL 등)
- 정교한 표/수식 파싱 (v1은 블록 탐지 수준)

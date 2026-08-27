# 2026-04-15 대화 요약

## 사용자 요청
- 현재 폴더 분석
- 프로젝트 확장 가능성 검토
- 논문 게시 여부 포함 평가
- 이후 Korean round-trip 결과가 왜 낮은지 확인
- 대화 내용을 markdown 파일로 저장

## 확인한 사항

### 프로젝트 성격
- 이 저장소는 단순 점자 변환기가 아니라 **데이터셋 + 파이프라인 + 웹서비스 + 논문 패키지**를 포함한 접근성 인프라 프로젝트로 판단됨.
- 중심 주제는 **KOSHA 한글 MSDS -> 한국어 점자 제공**.

### 논문 상태
- `README.md` citation에 `note={Submitted}` 존재.
- `paper/main.tex`에 `Manuscript submitted April 2026.` 존재.
- `paper/main.pdf` 존재.
- 따라서 레포 기준 가장 안전한 표현은 **submitted 상태**.
- accepted / published / DOI 등 게재 완료 증거는 확인하지 못함.

### 확장 가능성 핵심 정리
1. 인접 도메인 확장: KISCHEM first-aid, drug labels, food allergen
2. 접근성 코퍼스 팩토리화: 공통 schema 기반 생산 체계
3. CAS 기반 국제/이중언어 안전정보 플랫폼화
4. 웹 포털 제품화 강화
5. 논문/평가 재현성 강화
6. 후속 시리즈: pharmacy / law / emergency

### 검증 중 발견한 문제
- `pytest tests -q`로는 테스트가 수집되지 않음.
- `tests/test_braille_roundtrip.py --lang en`은 정상적으로 45/45 수준 결과 확인.
- `tests/test_braille_roundtrip.py --lang ko`는 낮은 점수를 보였음.

## Korean round-trip 저점수 원인 분석

### 1) 테스트 코드 문제
- `tests/test_braille_roundtrip.py`는 한국어 인코딩에 `encode_korean_braille()`를 쓰지만,
  decode 쪽은 `pipeline.decoder.braille_to_text()`를 그대로 사용함.
- 즉 한국어 전용 decoder (`pipeline.ko_braille_decoder.decode_korean_braille`)를 안 씀.
- 그래서 기존 `lang ko` 결과는 **잘못된 평가 경로**가 섞여 있음.

### 2) 한국어 전용 decoder를 써도 round-trip은 완벽하지 않음
- 직접 확인 결과:
  - 예시: `이것은 간단한 문장입니다.`
  - 한국어 전용 decoder 결과: `이것은 간단한 문장입니닾`
- golden set 45문장 기준 대략:
  - avg_edit ~ 0.7675
  - avg_chrf ~ 0.6595

### 3) 의미
- **KOSHA 한글 MSDS -> 점자 생성** 자체가 안 된다는 뜻은 아님.
- 현재 약한 부분은 주로 **점자 -> 한글 역변환(decoder)** 과 **그 평가 설계**.
- 다만, 만약 프로젝트의 중심 기능 주장에 **decoder / round-trip / validation robustness**가 포함된다면 그 부분은 현재 확실히 약점임.

## 사용자 우려에 대한 해석
- 사용자가 제기한 핵심 우려: “프로젝트 중심기능이 이상한 거 아냐?”
- 현재 판단:
  - **인코더 중심 서비스 기능**(한글 MSDS -> 점자)은 프로젝트 주 경로로 유지 가능.
  - 하지만 **한국어 decoder와 round-trip 검증 체계는 중심부 품질 이슈**로 봐야 함.
  - 따라서 '문제 없다'고 넘기면 안 되고, **핵심 품질 항목으로 수정 필요**.

## 제안된 30/60/90일 로드맵

### 0~30일
- KR round-trip 테스트를 한국어 decoder 기준으로 수정
- encoder 품질 / decoder ambiguity / eval 경로를 분리 보고
- README / RESULTS / paper / HF dataset card 수치 정합성 통일
- 설치/재현 환경 정리 (`pyproject.toml` 또는 requirements, DB path env 통일)

### 30~60일
- first-aid / allergen / drug-label mini release
- 웹 포털 pagination / deep link / bulk history
- 공통 schema 도입

### 60~90일
- CAS 기반 통합 accessibility record 구축
- inconvenience-emergency / pharmacy / law 확장
- 사용자 검증(user study) 및 논문 보강

## 저장 시점 결론
- 논문은 **submitted 상태로 보임**.
- 프로젝트는 확장 가치가 큼.
- 하지만 **KR decoder / round-trip / 테스트 체계는 실제 핵심 리스크**로 다뤄야 함.

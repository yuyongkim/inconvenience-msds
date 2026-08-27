# inconvenience 시리즈 확장 방안

KOSHA-Braille (inconvenience-msds) 이후 확장 경로.
각 항목은 독립 저장소 + 독립 논문으로 기획.

---

## 1. 즉시 확장 가능 (인코더 수정 불필요)

### inconvenience-pharmacy
- **소스**: 식품의약품안전처 의약품 허가정보 (data.go.kr)
- **대상**: 의약품 전문정보/환자용 설명서 (약 3만 품목)
- **선례**: EU Directive 2004/27/EC — 의약품 포장에 점자 의무화 (품목명만). 본 시스템은 전문 정보 전체를 대상으로 함.
- **현황**: FDA drug labels 3,795건 시범 export 완료 (data/domain_expansion/)
- **논문 전략**: UAIS 또는 Journal of the American Medical Informatics Association (JAMIA)

### inconvenience-food
- **소스**: 식품안전나라 API (식품의약품안전처)
- **대상**: 알레르겐 19개 카테고리, 영양성분표, 원재료명
- **현황**: 식품 알레르겐 19개 카테고리 template-based export 완료
- **논문 전략**: Food Control 또는 UAIS

### inconvenience-emergency
- **소스**: KISCHEM 응급처치 정보 (한국화학물질관리협회)
- **대상**: 화학사고 응급처치 7,189건
- **현황**: Braille export 완료 (data/domain_expansion/)
- **특이점**: 응급 상황 접근성 — 시각장애인 구조대원, 의료진 시나리오

---

## 2. 중기 확장 (도메인별 encoder 전문화 필요)

### inconvenience-law
- **소스**: 국가법령정보센터 Open API (법제처)
- **대상**: 산업안전보건법, 화학물질관리법, 장애인차별금지법 등
- **기술 요건**: 법령 특수 기호(조·항·호), 조문 구조 처리
- **전략적 가치**: 법·규제 자동화 트랙2와 직결 — 법 조문을 점자로 제공하는 것은 법률 접근성의 핵심
- **논문 전략**: Government Information Quarterly 또는 Law, Innovation and Technology

### inconvenience-standards
- **소스**: 국가표준원 (KS 표준), ISO 국제표준
- **대상**: 산업 안전 표준 문서
- **기술 요건**: 표, 수식, 도면 참조 처리

---

## 3. 장기 확장 (다국어, 타 규제 체계)

### inconvenience-osha (미국)
- **소스**: OSHA HazCom SDS (https://www.osha.gov/chemicaldata)
- **인코더**: English UEB (liblouis 기반, 이미 구현)
- **CAS 브릿지**: KOSHA ↔ OSHA 74,494개 공통 CAS number
- **전략**: 한국 → 미국 확장으로 "국제 표준" 주장 근거 확보

### inconvenience-reach (EU)
- **소스**: ECHA REACH 데이터베이스
- **인코더**: 각 EU 회원국 점자 표준 (22개국)
- **규모**: 등록 물질 ~23,000종

### inconvenience-j-check (일본)
- **소스**: 日本語 SDS (NITE, 化学物質総合情報提供システム)
- **인코더**: 일본 점자 (2001년 개정판)

---

## 4. 기술 로드맵

| 우선순위 | 항목 | 현재 상태 | 예상 공수 |
|---------|------|----------|----------|
| 1 | inconvenience-pharmacy | 3,795건 시범 완료 | 1주 (전체 export + 논문) |
| 2 | inconvenience-emergency | 7,189건 완료 | 3일 (논문만) |
| 3 | Grade 2 한국 점자 | 미구현 | 3-4주 (형태소 분석기 필요) |
| 4 | inconvenience-law | 미착수 | 2주 (법령 XML 파서) |
| 5 | 촉각 그래픽 (GHS 픽토그램) | 미착수 | 미정 |
| 6 | inconvenience-osha | 부분 구현 (EN 인코더) | 2주 |

---

## 5. 시리즈 공통 인프라

모든 inconvenience-* 저장소가 공유할 구조:

```
inconvenience-{domain}/
├── pipeline/
│   ├── ko_braille.py      # 공통 (inconvenience-msds에서 복사)
│   ├── extractor.py       # 도메인별 커스텀
│   └── domain_terms.py    # 도메인별 용어 사전
├── data/
│   └── hf_dataset/
├── web/                   # 참조 웹서비스 (공통 템플릿)
└── paper/
```

HuggingFace organization `Yuyongkim` 하위에 각 dataset 카드로 관리.

---

## 6. 논문 시리즈 전략

| 논문 | 저널/학회 | APC | 핵심 기여 |
|------|----------|-----|----------|
| inconvenience-msds (현재) | UAIS | $0 | 한국 화학안전 점자 코퍼스, 인프라 프레이밍 |
| inconvenience-pharmacy | UAIS 또는 JAMIA | $0 | 의약품 정보 접근성, EU 선례와 비교 |
| inconvenience-law | Government Information Quarterly | $0 | 법령 접근성, 장차법 Art.21 실증 |
| 시리즈 종합 | ASSETS 2027 | $0 | N=5+ user study 포함, 시리즈 전체 리뷰 |

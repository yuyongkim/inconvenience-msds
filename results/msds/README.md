# MSDS Braille Conversion Results

## Data Sources (from G:/MSDS project)

| Source | Count | Format | Content |
|--------|-------|--------|---------|
| NIOSH NPG | 73 | JSON | 상세 안전데이터 (PEL, IDLH, PPE, 증상 등) |
| CAS-CID map | 74,494 | JSON | 화학물질 식별번호 매핑 |
| ECHA CLP | ~4,400 | XLSX | EU 분류표시 (위험문구, 그림문자) |
| EPA list | TBD | XLSX | 미국 규제 화학물질 목록 |

## Completed

- `niosh_73_e2e.csv`: 73개 화학물질 전체 파이프라인 결과
  - 디코딩 정확도: 평균 99.0%, 최저 97.3%
  - EN text → EN braille → decode → correct → translate KR → KR braille

## Completed

- [x] KOSHA API 연동 (48,966개 한국어 MSDS, sections 1-16)
- [x] 48,963개 대량 변환 (127M chars → 247M braille chars, 3.3min)
- [x] GHS 위험문구 점자 변환 (H: 63개, P: 84개, 13,167 chemicals)
- [x] 한국어 MSDS 직접 점역 검증 (coverage 98.1%, 500 sample)

## Output Files

| File | Description |
|------|-------------|
| `bulk_stats.csv` | 48,963개 화학물질별 통계 (chem_id, name, text/braille chars) |
| `bulk_summary.json` | 대량 변환 집계 요약 |
| `ghs_h_statements.csv` | 63개 H-code → 한국어 → 한국어 점자 |
| `ghs_p_statements.csv` | 84개 P-code → 한국어 → 한국어 점자 |
| `ghs_summary.json` | GHS 통계 요약 |
| `kr_braille_validation.csv` | 500개 샘플 직접 점역 품질 검증 |
| `kr_braille_validation.json` | 검증 집계 요약 |

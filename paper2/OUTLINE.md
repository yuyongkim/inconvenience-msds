# Paper 2 — Outline (Draft v1)

## Working Title

**From a Single Catalog to a Public-Safety Braille Infrastructure: Extending KOSHA-Braille to Pharmaceuticals, Pesticides, and Industrial-Incident Case Records**

(Alt: *A Common Korean Braille Infrastructure for Public-Safety Information across Pharmaceuticals, Pesticides, and Industrial-Incident Records*)

## Series map (added 2026-08-25)

| Paper | Subject | Status |
|---|---|---|
| 1 | KOSHA-Braille, MSDS | published, UAIS (2026) 25:116 |
| 2 | pharmaceutical / pesticide / incident-record catalogues | this outline |
| 3 | transliteration root lexicon + cross-domain coverage | `paper3/OUTLINE.md` |
| 4 | cosmetics: non-aim scanning + ingredient summary | `paper4/OUTLINE.md` |
| 5 | Korean fingerspelling: person-independent evaluation | `paper5/OUTLINE.md` |

Paper 3 was split out rather than folded in here. This paper's contribution is
shipping catalogues; Paper 3 produces a lexicon and a measurement method and
ships no catalogue. It also does not depend on the data access this paper needs,
so it can proceed while catalogue keys are pending.

## Positioning vs Paper 1

| | Paper 1 (KOSHA-Braille) | Paper 2 |
|---|---|---|
| Domain | MSDS (occupational, 1 catalog) | Public-safety (3 catalogs spanning citizen / agricultural / industrial-incident dimensions) |
| Claim | Domain-deep validation | Cross-domain infrastructure validation |
| Contribution | Dataset + encoder + web service | Adapter framework + multi-catalog release + per-domain validation |
| Sec VIII status | Prospective extensibility | **Validated extensibility** (upgrade target) |

Paper 1 Sec VIII (`sec:extensibility`) explicitly listed pharmaceutical labels and first-aid protocols as prospective. Paper 2's job is to **promote those to validated** by actually shipping the catalogs. KOSHA disaster-case records close the loop with paper 1 (incidents → MSDS → prevention).

## Target Venue (recommended)

1. **UAIS — Universal Access in the Information Society** (Springer, continuation) — natural follow-up to Paper 1
2. **ACM TACCESS — Transactions on Accessible Computing** (alt) — stronger systems-paper framing

## Three Confirmed Domains

| # | Domain | API | Auth status | Records (est.) | Role in paper |
|---|---|---|---|---|---|
| D1 | **Pharmaceutical labels** | MFDS e약은요 (의약품안전나라) | ✅ active | ~35K | Citizen self-medication safety. Headline case study. |
| D2 | **Pesticide registrations** | PSIS 농약안전정보시스템 | ⏳ needs PSIS portal key | ~2K + safety guides | Rural / aging visual-impairment angle. GHS-adjacent. |
| D3 | **Industrial-incident cases** | KOSHA 국내재해사례 (data.go.kr 15121001) | ⏳ needs data.go.kr 활용신청 | ~hundreds (board posts) | Closes paper 1 loop (incidents ↔ MSDS); safety-training material. |

Dropped (and why):
- ~~AirKorea~~ — real-time stream shifts the paper toward HCI/systems; out of scope for catalog-based contribution.
- ~~초록누리 (household chemicals)~~ — OpenAPI requires business registration.
- ~~Food allergens~~ — 19-item prototype too small to support a separate contribution.

## Contributions (planned)

- **C1** — Multi-domain Korean braille catalog release: 3 public-safety domains, single HuggingFace dataset + per-domain configs
- **C2** — Common encoder + domain-adapter architecture (reuses paper-1 `ko_braille`, adds 3 lightweight adapters)
- **C3** — Per-domain quality validation (roundtrip, 2017 rule compliance, GHS / generic-name cross-references)
- **C4** — Domain-specific challenges report:
  - Pharma: drug brand vs generic, dosage forms, foreign drug names
  - Pesticide: crop × pest combinations, mixing ratios, withholding periods
  - Incident: free-form narrative text, named entities (workplace, equipment), tabular hazards
- **C5** — Cross-domain CAS / generic-name cross-reference (joins paper-1 MSDS to paper-2 catalogs)

## Sanity-Check Results (logged 2026-06-13)

Probes in `paper2/probes/`:

| Probe | Result | Notes |
|---|---|---|
| `probe_mfds.py` (e약은요) | ✅ 3/3 OK | 평균 1,512자 → 3,144셀, 비율 2.08 (paper-1 MSDS 1.95와 동등) |
| `probe_mfds_detail.py` (제품허가) | ❌ 500 | 활용신청 미등록 |
| `probe_psis.py` (농약) | ❌ ERR_101 | psis.rda.go.kr 자체 키 필요 |
| `probe_airkorea.py` | ❌ 403 | 활용신청 미등록 (도메인 자체 drop) |

## Section Plan (tentative)

```
I.    Introduction
        (motivation: same parity-of-access argument; expand from occupational
        to citizen and from registry to incident records)
II.   Related Work
        paper 1 + accessibility literature + Korean public-data landscape
III.  Domain Survey: 3 Korean Public-Safety APIs
IV.   Common Braille Infrastructure (paper-1 encoder reuse + adapter pattern)
V.    Domain Adapters
        V.A  Pharmaceutical (e약은요)
        V.B  Pesticide (PSIS)
        V.C  Industrial-Incident (KOSHA)
VI.   Dataset Statistics (per-domain + aggregate)
VII.  Validation
        VII.A Roundtrip per domain
        VII.B Korean braille rule compliance
        VII.C Cross-reference accuracy (CAS / generic name / incident → MSDS)
VIII. Discussion: Infrastructure-grade Accessibility, Revisited
        (the 3 domains together demonstrate that the same encoder serves
        radically different document shapes — structured tables, narrative
        text, and short safety-guide entries)
IX.   Limitations and Future Work
X.    Conclusion
```

## Prerequisite Actions (사장님)

1. **psis.rda.go.kr 가입 + OpenAPI 신청** — 농약등록정보 SVC01 (개인 가능, 사업자 무관)
2. **data.go.kr 활용신청 추가** — KOSHA 국내재해사례 (15121001), 기존 키 그대로 사용

활용목적 문구 예시: "학술논문 연구 — 시각장애인 정보 접근성 향상을 위한 한국어 점자 변환 데이터셋 구축 (UAIS 후속편)"

## Next Engineering Steps (after keys)

1. `scripts/paper2_fetch_drugs.py` — MFDS e약은요 bulk fetch + cache (rate-limited)
2. `scripts/paper2_fetch_pesticides.py` — PSIS bulk fetch (key-rate aware)
3. `scripts/paper2_fetch_incidents.py` — KOSHA disaster-case bulk fetch
4. `pipeline/adapters/{drug,pesticide,incident}.py` — adapter modules (text builder per domain)
5. `eval/paper2_validation.py` — per-domain roundtrip + rule check + cross-reference
6. `paper2/main.tex` — manuscript

## Open Questions

- KOSHA MSDS와의 CAS cross-reference: paper 2 안에 넣을지(D1·D2·D3 셋 다 cross-ref가능), paper 3로 미룰지 (현재 안: paper 2에 포함, contribution C5)
- 코드네임: **KSafe-Braille** vs **KOSHA-Braille-Extended** — 결정 보류

## Naming Convention

- Paper 1 = "KOSHA-Braille" (MSDS-specific brand)
- Paper 2 codename: **TBD**

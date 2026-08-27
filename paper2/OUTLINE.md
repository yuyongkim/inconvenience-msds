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
| D1 | **Pharmaceutical labels** | MFDS e약은요 **+ 제품허가(DrugPrdtPrmsnInfoService07)** | ✅ direct calls, no proxy | 3,052 collected | Citizen self-medication safety. Headline case study. |
| D2 | **Pesticide registrations** | 식품안전나라 `I1910` (**not** PSIS) | ✅ `Food` key in `.env` | 3,000 of 95,912 | Rural / aging visual-impairment angle. GHS-adjacent. |
| D3 | **Industrial-incident cases** | KOSHA `disaster_api02`, `callApiId=1060` (data.go.kr 15121001) | ✅ 2026-08-27 | 6,362 (whole board) | Closes paper 1 loop (incidents ↔ MSDS); the one narrative domain. |

Dropped (and why):
- ~~AirKorea~~ — real-time stream shifts the paper toward HCI/systems; out of scope for catalog-based contribution.
- ~~초록누리 (household chemicals)~~ — OpenAPI requires business registration.
- ~~Food allergens~~ — 19-item prototype too small to support a separate contribution.

## Contributions (planned)

- **C1** — Multi-domain Korean braille catalog release: 3 public-safety domains, single HuggingFace dataset + per-domain configs — **published 2026-08-27**, `Yuyongkim/inconvenience-public-safety`, 12,414 records / 9,603,528 braille cells. Push with `scripts/push_paper2_to_hf.py`.
- **C2** — Common encoder + domain-adapter architecture (reuses paper-1 `ko_braille`, adds 3 lightweight adapters)
- **C3** — Per-domain quality validation (roundtrip, 2017 rule compliance, GHS / generic-name cross-references)
- **C4** — Domain-specific challenges report:
  - Pharma: drug brand vs generic, dosage forms, foreign drug names
  - Pesticide: crop × pest combinations, mixing ratios, withholding periods
  - Incident: free-form narrative text, named entities (workplace, equipment), tabular hazards
- **C5** — Cross-domain cross-reference (joins paper-1 MSDS to paper-2 catalogs)
  — **done, and the answer is negative.** `scripts/paper2_cross_reference.py`,
  §7.4 of the draft. Whether a join is possible turns on which language the
  agency writes in, not on chemistry: drugs join at 0.0% in Korean and 46.3% in
  English, pesticides at 15.6% in Korean and 0.0% in English, and accident cases
  have no substance field at all (1.3% by incidental mention). The
  incident → MSDS → prevention loop paper 1 described does not close
  automatically.

## Sanity-Check Results (logged 2026-06-13)

Probes in `paper2/probes/`:

| Probe | Result | Notes |
|---|---|---|
| `probe_mfds.py` (e약은요) | ✅ 3/3 OK | 평균 1,512자 → 3,144셀, 비율 2.08 (paper-1 MSDS 1.95와 동등) |
| `probe_mfds_detail.py` (제품허가) | ~~❌ 500~~ → **✅ 동작** | 엔드포인트 버전이 07. ~~`chemip` 경유~~ → 직접 호출로 정정 (2026-08-27): 경유가 필요했던 것이 아니라 `.env` 파서가 인증키를 깨뜨리고 있었다 |
| `probe_psis.py` (농약) | ❌ ERR_101 → **도메인 자체가 다른 포털** | psis.rda.go.kr이 아니라 식품안전나라 `I1910` |
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

## Status update (2026-08-27) — three domains, all collected

All three domains are in. The manuscript drafts are `paper2/draft_ko.md` and
`paper2/draft_en.md`; figures are `paper2/figures/Fig1..3`.

| Domain | Source | Collected | Stability | Rule violations |
|---|---|---|---|---|
| 의약품 | MFDS 허가 + e약은요 (data.go.kr) | 3,052 (양쪽 서비스 1,682) | 100.0% | 0 |
| 농약 | 식품안전나라 I1910 | 3,000 of 95,912 | 100.0% | 0 |
| 산업재해 | KOSHA disaster_api02 | 6,362 (전량) | 99.8% | 0 |

합계 12,414건. 데이터셋 export는 `scripts/export_paper2_dataset.py`, 도메인마다
JSONL 한 개와 manifest 하나를 쓴다.

**D2 was not PSIS.** The outline listed 농약안전정보시스템 (psis.rda.go.kr) and a
separate portal key. The register that actually serves this data is 식품안전나라
(openapi.foodsafetykorea.go.kr), service `I1910`, and the key there is the
`Food` entry in `.env`.

**D3 endpoint.** `apis.data.go.kr/B552468/disaster_api02/getdisaster_api02`, with
`callApiId=1060`. The fixed value appears only in the activity guide attached to
the dataset page, not in the parameter list on the page itself.

**The key was never the problem.** Every direct data.go.kr call failed with
SERVICE_KEY_IS_NOT_REGISTERED_ERROR because the key in `.env` is stored quoted
and split across two lines, and a line-at-a-time parser truncated it. The error
names the key, so it reads as authorisation. `scripts/keys.py` parses the file
properly. The earlier remedy — routing the drug fetcher through the chemical
information service — was avoidance, not diagnosis: that service runs on this
machine and so leaves from the same address. It has been reverted to direct
calls. This is written up in §3.3 of the draft, because a later researcher will
hit the same wall.

**What the narrative domain found.** Adding incidents took stability from 100%
to 99.5% and exposed two real defects — a decoder that misread the roman
terminator across a word boundary, and an encoder that silently dropped
subscript digits (H₂S → "H S"). Both fixed. This is now the paper's main
argument (§8.1): extensibility is judged by what a new domain reveals, not by
whether it attaches.

**Validation sampling changed the numbers.** `validate` took the first 800
records of corpora that arrive ordered; incident records averaged 128 characters
that way against the corpus's 514. Now an even stride.

## Superseded status update (2026-08-26)


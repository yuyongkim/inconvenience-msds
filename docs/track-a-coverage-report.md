# Track A — root coverage across domains

Lexicon: 125 roots mined from KOSHA Korean/English name pairs (`data/morphology/roots.json`, built by `scripts/mine_morphemes.py`).

Coverage is the share of a name's Hangul that a known root accounts for. It says nothing about braille quality — the encoder already handles every name here. It measures how much of the naming vocabulary transfers.

## Summary

| Domain | Names | Char coverage | Fully covered | No root matched | Roots used |
|---|---:|---:|---:|---:|---:|
| KOSHA chemicals (source domain) | 9,903 | 40.4% | 4.4% | 25.7% | 118 |
| MFDS drug product names | 4,762 | 1.5% | 0.0% | 95.4% | 32 |
| WHO INN radicals (English) | 690 | 8.5% | 2.8% | 86.1% | 47 |
| KCIA cosmetic ingredients (Korean) | 1,380 | 12.5% | 0.1% | 71.2% | 68 |
| KCIA cosmetic ingredients (English INCI) | 1,291 | 15.9% | 1.2% | 62.4% | 83 |
| MFDS drug ingredients (Korean) | 1,650 | 8.1% | 0.1% | 76.1% | 65 |
| MFDS drug ingredients (English) | 1,650 | 14.7% | 0.6% | 59.1% | 71 |

## KOSHA chemicals (source domain)

Most-used roots:

| Root | Names |
|---|---:|
| methyl | 1,688 |
| propane | 794 |
| amine | 573 |
| ethyl | 566 |
| benzene | 537 |
| tetra | 523 |
| bis | 508 |
| chloro | 489 |
| phenyl | 479 |
| iso | 448 |
| hydroxy | 406 |
| butyl | 294 |
| chloride | 284 |
| acetate | 283 |
| fluoro | 278 |

Largest gaps — Hangul runs no root explains:

| Fragment | Names |
|---|---:|
| 다이 | 654 |
| 트리 | 190 |
| 트라이 | 169 |
| 폴리 | 143 |
| 나트륨 | 100 |
| 수화물 | 73 |
| 바이 | 72 |
| 에테르 | 65 |
| 암모늄 | 63 |
| 클로라이드 | 61 |
| 중합체 | 60 |
| 레이트 | 56 |
| 산염 | 56 |
| 펜산 | 52 |
| 메톡시 | 42 |
| 나트륨염 | 41 |
| 에탄올 | 41 |
| 에스테르 | 37 |
| 에스터 | 35 |
| 칼륨 | 34 |
| 렌디 | 32 |
| 알코올 | 30 |
| 페노에이트 | 28 |
| 니트로 | 27 |
| 시아네이트 | 27 |

## MFDS drug product names

Most-used roots:

| Root | Names |
|---|---:|
| propane | 55 |
| alpha | 31 |
| bis | 21 |
| beta | 16 |
| meta | 11 |
| amino | 10 |
| cresol | 9 |
| acetyl | 8 |
| amine | 6 |
| deca | 5 |
| para | 4 |
| oxide | 4 |
| gamma | 4 |
| iodide | 4 |
| carbonate | 3 |

Largest gaps — Hangul runs no root explains:

| Fragment | Names |
|---|---:|
| 연질캡슐 | 16 |
| 펜정밀리그램 | 9 |
| 마그 | 6 |
| 캡슐 | 5 |
| 펜연질캡슐 | 5 |
| 펜정밀리그람 | 4 |
| 온캡슐 | 4 |
| 트레스오릭스훠트정 | 3 |
| 펜정 | 3 |
| 에이 | 3 |
| 마그네슘정 | 3 |
| 팜젠 | 3 |
| 칼슘정 | 3 |
| 니코스탑패취 | 3 |
| 니코틴엘 | 3 |
| 나녹시딜액 | 3 |
| 노자임캡슐 | 3 |
| 펜시럽 | 3 |
| 도담도담츄어블정 | 3 |
| 디카본정 | 3 |
| 티라노골드플러스츄어블정 | 3 |
| 타치온정밀리그램 | 2 |
| 리나치올시럽 | 2 |
| 부루펜정밀리그램 | 2 |
| 포리부틴정 | 2 |

## WHO INN radicals (English)

Most-used roots:

| Root | Names |
|---|---:|
| sulfate | 7 |
| sulfo | 6 |
| hexa | 6 |
| oxo | 6 |
| amine | 5 |
| iso | 5 |
| acetate | 4 |
| penta | 4 |
| tetra | 4 |
| undecyl | 4 |
| sulfonate | 3 |
| decyl | 3 |
| propyl | 3 |
| methyl | 3 |
| oleate | 3 |

Largest gaps — Hangul runs no root explains:

| Fragment | Names |
|---|---:|

## KCIA cosmetic ingredients (Korean)

Most-used roots:

| Root | Names |
|---|---:|
| stearate | 67 |
| iso | 58 |
| methyl | 48 |
| propyl | 39 |
| ethyl | 36 |
| amide | 36 |
| hydroxy | 34 |
| acrylate | 29 |
| furan | 28 |
| hexa | 16 |
| amino | 16 |
| decyl | 16 |
| amine | 15 |
| tetra | 15 |
| penta | 15 |

Largest gaps — Hangul runs no root explains:

| Fragment | Names |
|---|---:|
| 레이트 | 53 |
| 다이 | 24 |
| 피이지 | 19 |
| 펩타이드 | 18 |
| 레이트코폴리머 | 11 |
| 쿼터늄 | 11 |
| 소듐 | 9 |
| 트라이 | 9 |
| 노녹시놀 | 9 |
| 펩타이드다이머 | 8 |
| 트라이데세스 | 7 |
| 피피지 | 7 |
| 에스에이치폴리펩타이드 | 6 |
| 알케인 | 6 |
| 에이트 | 6 |
| 알케스 | 6 |
| 메록사폴 | 6 |
| 적색호 | 6 |
| 에리스리틸 | 5 |
| 다이올크로스폴리머 | 5 |
| 피이지글리세릴아 | 5 |
| 소듐라우레스설페이트 | 5 |
| 에스알 | 4 |
| 에스에이치올리고펩타이드에스피 | 4 |
| 에스디엔에이압타머 | 4 |

## KCIA cosmetic ingredients (English INCI)

Most-used roots:

| Root | Names |
|---|---:|
| poly | 105 |
| iso | 57 |
| methyl | 52 |
| ethyl | 43 |
| stearate | 41 |
| propyl | 39 |
| hydroxy | 35 |
| amide | 33 |
| acrylate | 24 |
| carboxy | 23 |
| sulfate | 22 |
| amine | 22 |
| phosphate | 19 |
| oleate | 18 |
| hexa | 17 |

Largest gaps — Hangul runs no root explains:

| Fragment | Names |
|---|---:|

## MFDS drug ingredients (Korean)

Most-used roots:

| Root | Names |
|---|---:|
| propane | 73 |
| sulfate | 39 |
| meta | 27 |
| acetate | 24 |
| iso | 20 |
| bromide | 20 |
| phosphate | 20 |
| beta | 14 |
| amino | 14 |
| chloride | 14 |
| oxide | 13 |
| methyl | 13 |
| carbonate | 11 |
| nitrate | 10 |
| para | 9 |

Largest gaps — Hangul runs no root explains:

| Fragment | Names |
|---|---:|
| 아목시실린클라불란산칼륨 | 13 |
| 나트륨 | 10 |
| 덱사 | 8 |
| 스트 | 7 |
| 화물 | 7 |
| 컨티뉴에이션코오스 | 6 |
| 트리트먼트코오스 | 6 |
| 메톨론 | 5 |
| 설박탐나트륨암피실린나트륨 | 5 |
| 폴리 | 5 |
| 덱시부 | 4 |
| 말레 | 4 |
| 설박탐나트륨세포페라존나트륨 | 4 |
| 제이철착염 | 4 |
| 아목시실린수화물묽은클라불란산칼륨 | 4 |
| 소르비드 | 4 |
| 우라실 | 3 |
| 화수소산염 | 3 |
| 펜디씨 | 3 |
| 디클로페낙 | 3 |
| 에탄올 | 3 |
| 염수화물 | 3 |
| 미소 | 3 |
| 티아지드 | 3 |
| 세프타지딤수화물건조 | 3 |

## MFDS drug ingredients (English)

Most-used roots:

| Root | Names |
|---|---:|
| chloride | 325 |
| iso | 63 |
| sulfate | 46 |
| acetate | 43 |
| amine | 36 |
| amide | 33 |
| mono | 29 |
| poly | 28 |
| phosphate | 28 |
| methyl | 23 |
| bromide | 19 |
| beta | 18 |
| carbonate | 17 |
| meta | 16 |
| thio | 15 |

Largest gaps — Hangul runs no root explains:

| Fragment | Names |
|---|---:|

## What the pharmaceutical number means

The MFDS figure is low because the names are the wrong unit, not because the lexicon fails. DrbEasyDrugInfoService returns *product* names, and a brand name has no Latin root to find. The fragments the lexicon cannot explain are dosage form and strength: 연질캡슐, 캡슐, 정, 밀리그램.

Testing root transfer into pharmacy needs INN ingredient names, which live behind DrugPrdtPrmsnInfoService (주성분 / MAIN_ITEM_INGR). That endpoint returns HTTP 400 for the key this project holds; data.go.kr grants keys per service, so it has to be requested separately. Until then the pharmaceutical row measures brand naming and is not evidence either way about the lexicon.

The KOSHA row is the one that carries information: 40% of the Hangul in chemical names is accounted for by the mined roots. What is left is element names (나트륨, 칼륨), trivial names, and stems that did not clear the mining thresholds.

## What the cosmetics rows mean

The cosmetics dictionary gives both scripts for the same substance, which is why both rows are here. They agree closely (12.5% Korean against 15.9% English), so the limit is vocabulary in the lexicon rather than the transliteration step: if mapping into Hangul were the problem, the Korean row would sit well below the English one.

The gap to the source domain's 40% has two causes. Roughly 46% of cosmetic ingredient names are botanical, built from Korean plant names and 추출물, 꽃, 잎, 뿌리, which have no Latin root by construction; excluding them raises Korean coverage to 20.8%. The rest is orthographic: the two catalogues answer to different standards bodies and spell the same elements differently. Run `scripts/naming_convention_divergence.py` for that measurement.

## Expert-review candidates

The items below are what a Korean transliteration reviewer or a chemist would be asked to confirm. The unit of review is a single root, not a whole name, and this is not a full audit of the lexicon.

- Roots where the mined Korean form is a translation rather than a
  transliteration (`chloride` → 염화). These carry meaning, so a wrong
  one is a content error, not a spelling one.
- Roots kept on thin evidence (low corpus support in `roots.json`).
- The frequent gap fragments listed above: each is either a missing
  root or a genuine domain-specific term.

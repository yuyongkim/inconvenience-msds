# Paper 3 — Outline (Draft v1)

## Working Title

**What Korean Chemical Names Are Made Of: Mining a Transliteration Lexicon from
Aligned Regulatory Name Pairs, and What It Does Not Reach**

## Why this is not part of Paper 2

Paper 2 ships catalogues. Its contribution is an adapter framework, a
multi-catalogue release, and per-domain validation — it promotes Paper 1's
prospective extensibility to validated extensibility by actually publishing
pharmaceutical, pesticide and incident-record braille.

This paper ships no catalogue. It produces a lexicon and a measurement method,
and its central result is negative in a way that is worth reporting on its own.
Folding it into Paper 2 would bury both.

| | Paper 2 | Paper 3 |
|---|---|---|
| Artifact | three braille catalogues | a root lexicon + coverage method |
| Claim | extensibility is validated | naming vocabulary partially transfers, and here is how far |
| Unit of evaluation | per-domain braille quality | per-name morphological coverage |
| Depends on | catalogue access | aligned name pairs only |

Paper 3 is upstream of Paper 2 and does not need its data access.

## The gap this fills

The published encoder maps Hangul syllables to braille cells and never looks
inside a word. 디클로로디페닐트리클로로에탄 is transcribed syllable by syllable,
with no representation of 클로로 being *chloro* twice over.

That is correct for transcription. It cannot answer the question that decides
whether one accessibility resource extends across catalogues: do
pharmaceutical, cosmetic and pesticide names draw on the same Latin/Greek stock
as industrial chemicals? Answering it needs the roots identified first, and
nobody has published a Korean chemical transliteration lexicon derived from
data rather than from naming rules.

## Contributions

1. **A method for mining transliteration correspondences** from aligned
   Korean/English regulatory name pairs, with the three failure modes that
   decide whether it works: substring shadowing (*methyl* contains *ethyl*),
   length weighting (젠 beats 벤젠 on precision alone), and a minimum form
   length (single syllables identify nothing).

2. **A 125-root Korean chemical lexicon**, mined from 8,071 KOSHA name pairs.
   It contains translations as well as transliterations — *chloride* is 염화,
   not 클로라이드 — which a rule-derived lexicon would have missed.

3. **A cross-domain coverage measurement**, and the negative result: 40.4% of
   Hangul in chemical names is root-explained, and the pharmaceutical figure of
   1.5% measures the wrong strings rather than a failure to transfer.

4. **A documented data-access trap.** `DrbEasyDrugInfoService` returns product
   names; a public API that returns *something* for a drug query invites the
   assumption that it returns ingredients. The uncovered fragments — 연질캡슐,
   캡슐, 정, 밀리그램 — are the diagnostic.

## Target venue

1. **LREC** — a resource-and-method paper with a released lexicon fits directly.
2. **Language Resources and Evaluation** (journal) — same fit, longer form.
3. **UAIS** — possible, but the contribution is linguistic resource rather than
   accessibility system, which is a weaker fit than Papers 2 and 4.

## Status

| Component | State |
|---|---|
| Mining method | implemented, `scripts/mine_morphemes.py` |
| Lexicon | 125 roots, `data/morphology/roots.json` |
| Coverage measurement | implemented, `scripts/domain_coverage.py` |
| Chemical domain result | 40.4% char coverage over 9,903 names |
| Pharmaceutical result | measured, but on product names — needs ingredient access |
| INCI domain | not started |
| Pesticide domain | not started |
| Expert review of lexicon | not started, candidates listed |

## What has to happen before submission

- **Ingredient names.** `DrugPrdtPrmsnInfoService` (`MAIN_ITEM_INGR`) needs a
  separate data.go.kr service key. Without it the pharmaceutical row cannot
  carry the claim.
- **A second and third domain.** One domain plus a null result is not a
  cross-domain paper.
- **A transliteration reviewer** on the roots where the mined form is a
  translation. Those carry meaning, so an error is a content error.

## Drafted material

- `docs/track-a-coverage-report.md`
- `docs/track-a-followup-methods-draft.md`

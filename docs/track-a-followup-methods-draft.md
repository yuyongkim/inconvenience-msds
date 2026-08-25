# Track A — methods draft

Draft of the methods section for the follow-up paper. Covers the root lexicon
and the cross-domain coverage measurement only; the braille encoder is described
in the published paper and is unchanged here.

## Motivation

The published KOSHA-Braille encoder maps Hangul syllables to braille cells. It
never looks inside a word: 디클로로디페닐트리클로로에탄 is transcribed syllable
by syllable, with no notion that 클로로 is *chloro* occurring twice.

That is the right design for transcription and the wrong one for the question
this paper asks. Korean chemical, pharmaceutical, cosmetic and pesticide names
are transliterations of a shared Latin/Greek naming stock. If the same roots
recur across those catalogues, one accessibility resource can be extended to
all of them; if they do not, each catalogue needs its own vocabulary work. To
ask that, the roots have to be identified first.

## Building the lexicon

We did not write the lexicon by hand. The KOSHA database stores 8,071 chemicals
under both a Korean and an English name, and those pairs are evidence: if the
names containing *chloro* in English almost always contain 클로로 in Korean, and
names without it almost never do, the correspondence is real.

Candidate morphemes come from IUPAC substituent prefixes, multiplying prefixes,
functional-group suffixes and common ring stems, so every entry stays
interpretable. For each candidate we compare the Korean substring frequencies of
the names that contain it against those that do not, and keep a Korean form when
it separates the two sets.

Three details decide whether the result is usable.

**Substring shadowing.** *methyl* contains *ethyl*. Without masking, every
methyl- name enters ethyl's positive set and the shared Korean substring
collapses to 틸, which is the tail of both 메틸 and 에틸 and identifies neither.
Each candidate is therefore scored only where no longer candidate already claims
the same span.

**Length weighting.** Ranking by precision alone selects 젠 over 벤젠, because
unrelated names such as 다이페닐디아젠 also end in that syllable and cost the
longer form its precision. Scoring by separation times form length recovers the
whole transliteration.

**Minimum form length.** A single Hangul syllable is not evidence. 드 matched
333 names as the mined form of *-ide* and would match a large share of any
Korean corpus. Forms shorter than two syllables are discarded.

The lexicon that survives holds 125 roots. It contains translations as well as
transliterations: *chloride* appears as 염화, not 클로라이드. A hand-written
lexicon built from transliteration rules would have missed that, and 염화 is the
form Korean regulatory text uses.

## Coverage measurement

Coverage is the share of a name's Hangul that a known root accounts for, under a
greedy longest-match segmentation. It is a property of the name, not of the
braille: the encoder already transcribes every string in both catalogues.

| Domain | Names | Char coverage | Fully covered |
|---|---:|---:|---:|
| KOSHA chemicals (source) | 9,903 | 40.4% | 4.4% |
| MFDS drug product names | 4,762 | 1.5% | 0.0% |

## What the pharmaceutical row does and does not show

It does not show that the lexicon fails to transfer. It shows that we measured
the wrong strings. `DrbEasyDrugInfoService`, the only MFDS endpoint our
data.go.kr key is authorised for, returns product names — 활명수, 아네모정 —
which are brand names carrying no Latin root. The fragments the lexicon cannot
explain are dosage form and strength: 연질캡슐, 캡슐, 정, 밀리그램.

Ingredient names live behind `DrugPrdtPrmsnInfoService` under `MAIN_ITEM_INGR`.
That endpoint returns HTTP 400 for our key; data.go.kr authorises keys per
service, so access has to be requested separately. Until it is, the
pharmaceutical row measures Korean brand naming and should be reported as such.

This is worth stating plainly rather than dropping, because the failure mode is
easy to repeat: a public API that returns *something* for a drug query invites
the assumption that it returns ingredients.

## Limitations

- The source domain reaches 40%, not more. The remainder is element names
  (나트륨, 칼륨), trivial names with no compositional structure, and stems that
  did not clear the mining thresholds. Raising coverage means extending the
  candidate list, not changing the method.
- Segmentation is greedy and longest-match, so a name that could be split two
  ways is not disambiguated.
- The lexicon is mined from one regulatory corpus and reflects its
  transliteration conventions. Another corpus may spell the same root
  differently (뷰틸 / 부틸).
- No human transliteration reviewer has checked the lexicon. Candidates for that
  review are listed in `track-a-coverage-report.md`.

## Reproduction

```
python scripts/mine_morphemes.py      # rebuilds data/morphology/roots.json
python scripts/domain_coverage.py     # rebuilds docs/track-a-coverage-report.md
```

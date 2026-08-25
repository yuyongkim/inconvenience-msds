# What Korean Chemical Names Are Made Of: Mining a Transliteration Lexicon from Aligned Regulatory Name Pairs, and What It Does Not Reach

Yuyong Kim
University of Wisconsin-Madison, Madison, WI 53706, USA
Email: ykim288@wisc.edu
ORCID: 0009-0006-4842-666X

---

## Abstract

**Purpose.** Korean chemical names are transliterations of Latin- and Greek-derived English ones. If the same roots recur in pharmaceutical, cosmetic and pesticide names, one accessibility resource can be extended across regulatory catalogues; if not, each catalogue needs its own vocabulary work. This report presents a root lexicon and a measurement method for answering that question.

**Methods.** Rather than deriving the lexicon from naming rules, we mined it statistically from 8,071 aligned Korean/English name pairs in the KOSHA database. Candidate morphemes were taken from IUPAC nomenclature. For each candidate we compared Korean substring frequencies between the names containing it and those not, and kept the correspondences that separated the two sets. Coverage of the resulting lexicon was then measured over three domains.

**Results.** The method yields 125 roots. Across 9,903 KOSHA chemical names, 40.4% of the Hangul is accounted for by a known root. WHO INN radicals (690 names) reach 8.5% and MFDS drug names (4,762) reach 1.5%. The lexicon contains translations as well as transliterations: *chloride* appears as 염화, not 클로라이드.

**Conclusions.** The low pharmaceutical figure is not a failure of transfer but a failure of measurement. The only accessible public endpoint returns product names rather than ingredient names, and the fragments left unexplained — 연질캡슐, 캡슐, 정, 밀리그램 — diagnose exactly that. We release the lexicon and the method, and document the trap of not checking what a public API actually returns.

**Keywords:** transliteration lexicon; morphological decomposition; chemical nomenclature; regulatory data; accessibility infrastructure; domain extension

---

## 1. Introduction

The published KOSHA-Braille encoder maps Hangul syllables to braille cells [1]. It never looks inside a word: 디클로로디페닐트리클로로에탄 is transcribed syllable by syllable, and the fact that 클로로 is *chloro* occurring twice is not represented anywhere.

That is correct for transcription. It cannot answer the question that decides whether an accessibility resource extends across domains: do pharmaceutical, cosmetic and pesticide names draw on the same Latin/Greek stock as industrial chemicals? Answering it requires the roots to be identified first.

Normative descriptions of Korean chemical transliteration exist in Korean Chemical Society nomenclature, but no lexicon derived from the transliterations that regulatory documents actually use has been published. Norm and practice diverge in places (Section 4.2), and those places carry the more useful information.

This report contributes four things.

1. A method for mining transliteration correspondences from aligned regulatory name pairs, and the three conditions that decide whether it works.
2. A 125-root Korean chemical lexicon mined from 8,071 KOSHA pairs.
3. A coverage measurement over three domains, and its interpretation.
4. A documented trap concerning what a public API returns.

## 2. Related work

Machine transliteration has been studied largely for proper nouns. In chemical nomenclature, parsing IUPAC names into structures [2] is established, but that recovers molecular structure from English names and does not address transliterated non-Latin-script names.

We are not aware of morphological decomposition work targeting Korean chemical names. In the accessibility literature, braille conversion is treated as character-level mapping [1], and the internal structure of names is not considered.

## 3. Methods

### 3.1 Data

The `chemical_terms` table of the KOSHA database records each chemical under both a Korean and an English name. Of 117,744 rows, 111,556 carry an English name, but only 8,071 carry actual Hangul in the Korean-name field; the rest repeat the English name there. This study uses those 8,071 pairs.

Names were normalised by removing parenthetical annotations (English glosses, trivial names) and locant or stereo descriptors (1,2-, (E)-, N,N'-), then keeping only Hangul or Latin letters.

### 3.2 Mining

Candidate morphemes were taken from IUPAC substituent prefixes, multiplying prefixes, functional-group suffixes and ring stems. Taking candidates from nomenclature rather than guessing them keeps every lexicon entry interpretable.

For each candidate, the Korean counterparts of names containing it (positives) were separated from those not containing it (negatives), and Korean substrings frequent among positives and rare among negatives were taken as correspondence candidates.

### 3.3 Three conditions that decide the outcome

The method itself is unremarkable. What decides the result is the following (Fig. 2).

**Substring shadowing.** *methyl* contains *ethyl*. Without masking, every methyl- name enters ethyl's positive set and the shared substring collapses to 틸, the common tail of 메틸 and 에틸, which identifies neither. Each candidate is therefore counted only at positions no longer candidate already claims.

**Length weighting.** Ranking by precision alone selects 젠 over 벤젠, because names without *benzene* — 다이페닐디아젠 among them — end in the same syllable and cost the longer form its precision. Scoring separation times form length recovers the whole transliteration.

**Minimum form length.** A single syllable is not evidence. 드, mined as the form of *-ide*, appeared in 333 names and would match a large share of any Korean corpus. Forms shorter than two syllables were discarded.

### 3.4 Coverage

Coverage is the share of a name's Hangul explained by a known root under greedy longest-match segmentation. It is a property of the name, not of the braille: the encoder already transcribes every string in both catalogues.

## 4. Results

### 4.1 The lexicon

125 roots survive (Table 1). Ranked by corpus support: methyl (1,131), ethyl (466), amine (455), bis (426), iso (423).

**Table 1.** Root coverage by domain

| Domain | Names | Char coverage | Fully covered | Roots used |
|---|---:|---:|---:|---:|
| KOSHA chemicals (source) | 9,903 | 40.4% | 4.4% | 118 |
| WHO INN radicals (English) | 690 | 8.5% | 2.8% | 47 |
| MFDS drug product names | 4,762 | 1.5% | 0.0% | 32 |

### 4.2 Correspondences that are not transliterations

The lexicon contains translations as well as transliterations. *chloride* was mined as 염화 rather than 클로라이드, confirmed across 346 names. A lexicon deduced from transliteration rules could not have produced that entry. It emerged because the lexicon was mined from data, and 염화 is the form Korean regulatory text uses.

Such entries carry meaning, so an error in one is a content error rather than a spelling error. They are listed separately among the expert-review candidates in Section 6.

### 4.3 Interpreting the pharmaceutical figure

The MFDS figure of 1.5% does not show that the lexicon fails to transfer. It shows that the wrong strings were measured.

`DrbEasyDrugInfoService`, the only MFDS endpoint our data.go.kr key is authorised for, returns product names. Brand names such as 활명수 and 아네모정 contain no Latin root. The diagnostic is that the largest unexplained fragments are 연질캡슐, 캡슐, 정 and 밀리그램: dosage form and strength.

Ingredient names live in the `MAIN_ITEM_INGR` field of `DrugPrdtPrmsnInfoService`, which returns HTTP 400 for our key. data.go.kr authorises keys per service, so access must be requested separately.

We record this rather than omitting it because the failure mode is easy to repeat: a public API that returns *something* for a drug query invites the assumption that it returns ingredients.

## 5. Discussion

The source-domain figure of 40.4% is not a ceiling. What remains unexplained is element names (나트륨, 칼륨), trivial names with no compositional structure, and stems that did not clear the mining thresholds. Raising coverage means extending the candidate list, not changing the method.

The INN figure of 8.5% was measured against English roots. Korean transliterations of those names were not obtainable, so the number shows only that the roots themselves recur, not that transliteration transfers.

## 6. Limitations

- The lexicon is mined from one regulatory corpus and reflects its transliteration conventions. Another corpus may spell the same root differently (뷰틸 / 부틸).
- Segmentation is greedy longest-match, so ambiguous decompositions are not resolved.
- No transliteration reviewer has checked the lexicon.

### Expert-review candidates

The unit of review is a single root, not a whole name, and this is not a full audit.

- Roots mined as translations rather than transliterations (*chloride* → 염화). These carry meaning, so the nature of an error differs.
- Roots kept on low corpus support.
- Frequent unexplained fragments, each either a missing root or a genuine domain term.

## 7. Conclusion

Aligned regulatory name pairs are evidence for a transliteration lexicon. We release the method, the conditions that decide its outcome, and the resulting 125 roots. The principal result across three domains is not positive transfer but the observation that failing to check what a public API returns produces a measurement that reads as failed domain transfer.

## Reproduction

```
python scripts/mine_morphemes.py      # rebuilds data/morphology/roots.json
python scripts/domain_coverage.py     # rebuilds docs/track-a-coverage-report.md
```

## References

[1] Kim, Y. (2026). KOSHA-Braille: infrastructure-grade accessibility for Korean chemical safety information. *Universal Access in the Information Society*, 25, 116. https://doi.org/10.1007/s10209-026-01381-0

[2] IUPAC. *Nomenclature of Organic Chemistry: Recommendations and Preferred Names*. Royal Society of Chemistry, 2013.

[3] World Health Organization. *International Nonproprietary Names (INN) for Pharmaceutical Substances: Names for Radicals, Groups and Others*. WHO/EMP/RHT/TSN/2015.1.

---

## Figures

**Fig. 1** Reach of the 125-root lexicon by domain. Bars give the share of each catalogue's name characters explained by a known root. The MFDS bar is short because the strings measured are product names, not ingredient names. (`figures/Fig1.png`)

**Fig. 2** The three conditions that decide whether mining works. Each row is a real corpus case: the naive result on the left, the corrected result on the right. (`figures/Fig2.png`)

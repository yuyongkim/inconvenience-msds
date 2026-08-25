# What Korean Chemical Names Are Made Of: Mining a Transliteration Lexicon from Aligned Regulatory Name Pairs, and What It Does Not Reach

Yuyong Kim
University of Wisconsin-Madison, Madison, WI 53706, USA
Email: ykim288@wisc.edu
ORCID: 0009-0006-4842-666X

---

## Abstract

**Purpose.** Korean chemical names are transliterations of Latin- and Greek-derived English ones. If the same roots recur in pharmaceutical, cosmetic and pesticide names, one accessibility resource can be extended across regulatory catalogues; if not, each catalogue needs its own vocabulary work. This report presents a root lexicon and a measurement method for answering that question.

**Methods.** Rather than deriving the lexicon from naming rules, we mined it statistically from 8,071 aligned Korean/English name pairs in the KOSHA database. Candidate morphemes were taken from IUPAC nomenclature. For each candidate we compared Korean substring frequencies between the names containing it and those not, and kept the correspondences that separated the two sets. Coverage of the resulting lexicon was then measured over four domains, including a 1,380-entry sample of the Korean cosmetic ingredient dictionary, which gives Korean and English names for the same substance and so separates vocabulary transfer from spelling transfer.

**Results.** The method yields 125 roots. Across 9,903 KOSHA chemical names, 40.4% of the Hangul is accounted for by a known root. Cosmetic ingredient names reach 12.5% on the Korean side and 15.9% on the English, WHO INN radicals (690 names) reach 8.5%, and MFDS drug names (4,762) reach 1.5%. The roots themselves transfer: methyl, ethyl, propyl, stearate, hydroxy and acrylate occur at comparable rates in both catalogues. The spellings do not. KOSHA writes sodium and potassium as 나트륨 and 칼륨, following the Korean Chemical Society; the cosmetics dictionary writes 소듐 and 포타슘, following the English INCI. Neither KOSHA form occurs even once in the cosmetics sample.

**Conclusions.** Cross-domain transfer succeeds and fails in different places, and the distinction is the result: chemical vocabulary is shared, orthographic convention belongs to whichever body maintains the register. A lexicon mined in one catalogue therefore under-reads in another for reasons that are administrative rather than chemical, and a Korean reader meets two official spellings of the same element depending on which label is in their hand. The low pharmaceutical figure is separately a failure of measurement rather than of transfer: the only accessible public endpoint returns product names, and the unexplained fragments — 연질캡슐, 캡슐, 정, 밀리그램 — diagnose exactly that.

**Keywords:** transliteration lexicon; morphological decomposition; chemical nomenclature; regulatory data; accessibility infrastructure; domain extension; orthographic convention

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

**The cosmetics catalogue.** The Korean Cosmetic Association publishes a
dictionary of cosmetic ingredients giving, for each entry, a standardised
Korean name, the English INCI name and a CAS number [4]. This is the domain
that tests transfer properly, because it names the same kind of substance from
the same Latin and Greek stock and supplies both scripts for it, so vocabulary
and orthography can be separated.

The dictionary holds roughly 24,900 entries. We sampled 1,380 of them on a
fixed page stride rather than taking a census, which is enough for a rate and
leaves the association's server alone. Their terms of use vest copyright in the
association and prohibit commercial reproduction or redistribution, so the
sample is held locally and never committed; what this study publishes is
statistics computed from it. Redistributing the pairs would require the
association's prior consent, which we have not sought.

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
| KCIA cosmetic ingredients (English INCI) | 1,291 | 15.9% | 1.2% | 68 |
| KCIA cosmetic ingredients (Korean) | 1,380 | 12.5% | 0.1% | 61 |
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

### 4.4 Cosmetics: the roots transfer, the spellings do not

The cosmetics dictionary answers the question the pharmaceutical row could not, because it supplies ingredient names in both scripts.

The roots transfer. Measured as whole tokens, the shared chemical vocabulary appears in both catalogues at comparable rates (Fig. 3, left).

**Table 2.** Shared roots, share of names containing each. KOSHA n = 9,903; KCIA sample n = 1,380.

| Root | KOSHA | KCIA cosmetics |
|---|---:|---:|
| 메틸 (methyl) | 14.79% | 3.41% |
| 에틸 (ethyl) | 7.70% | 3.48% |
| 하이드록시 (hydroxy) | 3.97% | 2.39% |
| 프로필 (propyl) | 2.27% | 2.90% |
| 아크릴 (acryl) | 1.46% | 1.52% |
| 스테아 (stear) | 0.69% | 4.42% |

The ordering shifts with what each industry actually uses. Stearates are emollients and surfactants, so they are six times commoner in cosmetics. The vocabulary is nonetheless the same vocabulary.

The spellings do not transfer. The two catalogues are maintained by different bodies with different romanisation ancestries, and for element names they do not overlap at all.

**Table 3.** Element and prefix spellings by catalogue. Elements matched as whole tokens; prefixes at name-initial position only, since as substrings they match unrelated names.

| English | Form | KOSHA | KCIA cosmetics |
|---|---|---:|---:|
| sodium | 나트륨 | 5.08% | **0.00%** |
| sodium | 소듐 | 0.76% | 4.42% |
| potassium | 칼륨 | 1.30% | **0.00%** |
| potassium | 포타슘 | 0.15% | 1.09% |
| di- | 디 | 5.00% | 0.14% |
| di- | 다이 | 5.38% | 4.49% |
| tri- | 트리 | 2.42% | 0.14% |
| tri- | 트라이 | 1.81% | 1.74% |

Not one of the 1,380 cosmetic ingredient names contains 나트륨 or 칼륨. KOSHA follows the Korean Chemical Society, which kept the German-derived element names that entered Korean scientific vocabulary through Japanese; the cosmetics dictionary transliterates the English INCI directly. The prefixes tell the same story more softly: KOSHA uses 디 and 다이 in almost equal measure, so it is internally inconsistent, while the cosmetics dictionary has settled on 다이.

This is why the Korean cosmetics figure sits at 12.5% rather than near the source domain's 40.4%. It is not that the chemistry is unfamiliar. A lexicon mined from one registry inherits that registry's house style, and 45.8% of cosmetic ingredient names are botanical besides, built from Korean plant names and the words 추출물, 꽃, 잎, 뿌리, which have no Latin root by construction. Excluding botanicals raises Korean coverage to 20.8%.

The Korean and English sides agree closely, 12.5% against 15.9%, which locates the limit. If the transliteration step were the problem, the Korean side would fall well below the English one. It does not, so what is missing is vocabulary in the lexicon, not the mapping into Hangul.

## 5. Discussion

The source-domain figure of 40.4% is not a ceiling. What remains unexplained is element names (나트륨, 칼륨), trivial names with no compositional structure, and stems that did not clear the mining thresholds. Raising coverage means extending the candidate list, not changing the method.

The INN figure of 8.5% was measured against English roots. Korean transliterations of those names were not obtainable, so the number shows only that the roots themselves recur, not that transliteration transfers.

### 5.1 Two registries, one language, two spellings

The element result is small to state and awkward to live with. A Korean reader who meets sodium lauryl sulfate on a shampoo bottle and sodium hydroxide on a safety data sheet is given two different Korean words for the same element, by two public bodies, in the same language. Neither body is wrong within its own register. 나트륨 is standard chemical Korean, 소듐 is the standard cosmetics transliteration, and both are officially maintained.

For a sighted reader the cost is a moment's friction. For the accessibility case this series argues, it is more than that. Braille and speech both flatten the visual cues that would let a reader guess the two forms are the same substance, and someone assembling a list of ingredients to avoid has no way to know that the 소듐 on one label and the 나트륨 on another are one thing.

The engineering consequence is narrow and useful. A cross-domain lexicon needs variant spellings recorded as alternates of one root, not one canonical spelling per root. That is a schema decision, and it has to be made before the lexicon is built rather than patched afterwards.

We do not propose that either body change its convention. Both are settled, and an accessibility project is not the right instrument for standardising a national scientific vocabulary.

## 6. Limitations

- The lexicon is mined from one regulatory corpus and reflects its transliteration conventions. Section 4.4 measures that limitation rather than removing it: the lexicon still holds one spelling per root.
- The cosmetics figure comes from a 1,380-entry sample, not a census. Sampling was by fixed page stride, which is unbiased with respect to the dictionary's ordering but is still a sample.
- The cosmetics dictionary's terms prohibit redistribution, so the sample cannot be released with the paper. Only the statistics and the fetching script are reproducible, and a reader re-running the script draws their own sample, so rates should be expected to move by a fraction of a point.
- Segmentation is greedy longest-match, so ambiguous decompositions are not resolved.
- No transliteration reviewer has checked the lexicon.

### Expert-review candidates

The unit of review is a single root, not a whole name, and this is not a full audit.

- Roots mined as translations rather than transliterations (*chloride* → 염화). These carry meaning, so the nature of an error differs.
- Roots kept on low corpus support.
- Frequent unexplained fragments, each either a missing root or a genuine domain term.

## 7. Conclusion

Aligned regulatory name pairs are evidence for a transliteration lexicon. We release the method, the conditions that decide its outcome, and the resulting 125 roots.

Across four domains the result splits in two. Chemical vocabulary crosses the boundary between registries: the same roots name industrial chemicals and cosmetic ingredients, at comparable rates, in both scripts. Orthographic convention does not cross it, and for element names it does not overlap at all, because each register answers to a different standards body. A lexicon built for one catalogue will under-read in another for reasons that have nothing to do with chemistry, and the fix is a schema that stores variant spellings per root rather than a canonical one.

The pharmaceutical row remains a separate lesson: failing to check what a public API returns produces a measurement that reads as failed domain transfer.

## Reproduction

```
python scripts/mine_morphemes.py                  # rebuilds data/morphology/roots.json
python scripts/fetch_kcia_sample.py               # samples the cosmetics dictionary
python scripts/domain_coverage.py                 # rebuilds docs/track-a-coverage-report.md
python scripts/naming_convention_divergence.py    # Tables 2 and 3
```

`fetch_kcia_sample.py` writes to `data/kcia_cache/`, which is gitignored under the dictionary's terms of use. Everything downstream reads statistics, not entries.

## References

[1] Kim, Y. (2026). KOSHA-Braille: infrastructure-grade accessibility for Korean chemical safety information. *Universal Access in the Information Society*, 25, 116. https://doi.org/10.1007/s10209-026-01381-0

[2] IUPAC. *Nomenclature of Organic Chemistry: Recommendations and Preferred Names*. Royal Society of Chemistry, 2013.

[3] World Health Organization. *International Nonproprietary Names (INN) for Pharmaceutical Substances: Names for Radicals, Groups and Others*. WHO/EMP/RHT/TSN/2015.1.

[4] 대한화장품협회 [Korean Cosmetic Association]. *화장품 성분사전* [Cosmetic Ingredient Dictionary]. https://kcia.or.kr/cid

[5] 대한화학회 [Korean Chemical Society]. *화합물 명명법* [Nomenclature of Chemical Compounds].

---

## Figures

**Fig. 1** Reach of the 125-root lexicon by domain. Bars give the share of each catalogue's name characters explained by a known root. The MFDS bar is short because the strings measured are product names, not ingredient names. (`figures/Fig1.png`)

**Fig. 2** The three conditions that decide whether mining works. Each row is a real corpus case: the naive result on the left, the corrected result on the right. (`figures/Fig2.png`)

**Fig. 3** The two halves of the cross-domain result. Left: shared chemical roots occur in both catalogues at comparable rates. Right: the same two elements are spelled one way by KOSHA and the other by the cosmetics dictionary, with no overlap. Prefixes are counted at name-initial position only. (`figures/Fig3.png`)

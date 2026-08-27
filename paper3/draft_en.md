# What Korean Chemical Names Are Made Of: A Mined Transliteration Lexicon and the Registry Conventions It Cannot Cross

Yuyong Kim
University of Wisconsin-Madison, Madison, WI 53706, USA
Email: ykim288@wisc.edu
ORCID: 0009-0006-4842-666X

---

## Abstract

**Purpose.** Korean chemical names are transliterations of Latin- and Greek-derived English ones. If the same roots recur in pharmaceutical, cosmetic and pesticide names, one accessibility resource can be extended across regulatory catalogues; if not, each catalogue needs its own vocabulary work. This report presents a root lexicon and a measurement method for answering that question.

**Methods.** Rather than deriving the lexicon from naming rules, we mined it statistically from 8,071 aligned Korean/English name pairs in the KOSHA database. Candidate morphemes were taken from IUPAC nomenclature. For each candidate we compared Korean substring frequencies between the names containing it and those not, and kept the correspondences that separated the two sets. Coverage of the resulting lexicon was then measured over five domains across three Korean regulatory registries, using catalogues that give Korean and English names for the same substance and so separate vocabulary transfer from spelling transfer: 1,380 entries from the cosmetic ingredient dictionary and 1,650 drug ingredient names from the MFDS approval register.

**Results.** The method yields 125 roots. Across 9,903 KOSHA chemical names, 40.4% of the Hangul is accounted for by a known root. Cosmetic ingredient names reach 12.5% on the Korean side and 15.9% on the English; drug ingredient names reach 8.1% and 14.7%. The roots themselves transfer, occurring in all three registries at comparable rates. The spellings do not, and the divergence is systematic rather than incidental. Pharmacy and cosmetics do not overlap at all on the elements sodium and potassium: drugs write 나트륨 and 칼륨, cosmetics write 소듐 and 포타슘, and each form is absent from the other register. The same split runs deeper than element names. Cosmetics transliterates counter-ions (설페이트, 포스페이트) and never translates them; pharmacy translates them into Sino-Korean (황산, 염산, 수화물) and rarely transliterates. KOSHA, the registry this lexicon was mined from, is the only one of the three that uses both.

**Conclusions.** Cross-registry transfer succeeds and fails in different places, and the distinction is the result: chemical vocabulary is shared, orthographic convention belongs to whichever body maintains the register. A lexicon mined in one catalogue under-reads in another for reasons that are administrative rather than chemical, and a Korean reader meets two official spellings of the same substance depending on which label is in their hand. The pharmaceutical figure also settles a question the earlier version of this work could only diagnose: measured on product names the same lexicon reached 1.5%, and measured on ingredient names from the same agency it reaches 8.1%, so the low figure was a failure of measurement rather than of transfer.

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

**The pharmaceutical catalogue.** Section 4.3 of an earlier version of this
report argued that the pharmaceutical row measured the wrong strings, because
the only endpoint then reachable returned product names. The ingredient names
live in the MFDS drug approval register, and this study reads them through the
authorised key, calling the register directly.

The register has no listing call, only substring search on the product name, so
we swept the dosage-form words that nearly every Korean product name contains
(정, 캡슐, 주사 …) and deduplicated by item. That yielded 12,633 distinct
products and, from them, 1,650 ingredient names.

Korean generic products print the active ingredient in parentheses after the
product name — 보령아스트릭스캡슐100밀리그람(아스피린) — and the English
ingredient arrives as its own field, so the pair comes out of one record. That
is the same shape as the cosmetics dictionary, reached by a different route.

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
| MFDS drug ingredients (English) | 1,650 | 14.7% | 0.6% | 71 |
| KCIA cosmetic ingredients (Korean) | 1,380 | 12.5% | 0.1% | 61 |
| WHO INN radicals (English) | 690 | 8.5% | 2.8% | 47 |
| MFDS drug ingredients (Korean) | 1,650 | 8.1% | 0.1% | 65 |
| MFDS drug *product* names | 4,762 | 1.5% | 0.0% | 32 |

### 4.2 Correspondences that are not transliterations

The lexicon contains translations as well as transliterations. *chloride* was mined as 염화 rather than 클로라이드, confirmed across 346 names. A lexicon deduced from transliteration rules could not have produced that entry. It emerged because the lexicon was mined from data, and 염화 is the form Korean regulatory text uses.

Such entries carry meaning, so an error in one is a content error rather than a spelling error. They are listed separately among the expert-review candidates in Section 6.

### 4.3 The pharmaceutical figure, measured twice

An earlier version of this report gave the pharmaceutical row as 1.5% and argued that the number described the measurement rather than the lexicon. `DrbEasyDrugInfoService`, the only MFDS endpoint then reachable, returns product names, and brand names such as 활명수 and 아네모정 contain no Latin root. The diagnostic offered was that the largest unexplained fragments were 연질캡슐, 캡슐, 정 and 밀리그램: dosage form and strength, not chemistry.

That argument can now be tested rather than asserted, because the ingredient names from the same agency are in hand.

**Table 2.** The same lexicon against two readings of the same catalogue.

| Strings measured | Names | Char coverage |
|---|---:|---:|
| Product names (`DrbEasyDrugInfoService`) | 4,762 | 1.5% |
| Ingredient names (approval register) | 1,650 | 8.1% |

Coverage rises by a factor of five on the same lexicon and the same agency. The diagnosis holds: the earlier figure measured brand naming.

We keep both rows in Table 1 rather than replacing one with the other. The product-name row is not a mistake to be corrected out of the record — it is the measurement a reader would get from the endpoint that is easiest to reach, and the gap between the two rows is the finding.

What the ingredient row does not do is rise to the source domain's 40.4%. Section 4.4 takes up why.

### 4.4 The roots transfer, the spellings do not

With two ingredient catalogues in hand the question splits cleanly, because both give Korean and English names for the same substances.

The roots transfer. Measured as whole tokens, the shared chemical vocabulary appears in all three registries (Fig. 3, left).

**Table 3.** Shared roots, share of names containing each. KOSHA n = 9,903; MFDS ingredients n = 1,650; KCIA sample n = 1,380.

| Root | KOSHA | MFDS drugs | KCIA cosmetics |
|---|---:|---:|---:|
| 메틸 (methyl) | 14.79% | 0.79% | 3.41% |
| 에틸 (ethyl) | 7.70% | 0.55% | 3.48% |
| 아미노 (amino) | 2.66% | 0.85% | 1.16% |
| 벤조 (benzo) | 2.62% | 0.48% | 0.58% |
| 프로필 (propyl) | 2.27% | 0.24% | 2.90% |
| 아세테이트 (acetate) | 0.64% | 0.85% | 0.94% |

Rates shift with what each industry uses — stearates are emollients, so they are six times commoner in cosmetics than in industrial chemicals, and alkyl prefixes are rarer in pharmacy, whose names are built from INN stems — but the vocabulary is the same vocabulary.

The spellings do not transfer, and the divergence is not a matter of degree.

**Table 4.** Element and prefix spellings by registry. Elements matched as whole tokens; prefixes at name-initial position only, since as substrings they match unrelated names.

| English | Form | KOSHA | MFDS drugs | KCIA cosmetics |
|---|---|---:|---:|---:|
| sodium | 나트륨 | 5.08% | 9.64% | **0.00%** |
| sodium | 소듐 | 0.76% | **0.00%** | 4.42% |
| potassium | 칼륨 | 1.30% | 2.06% | **0.00%** |
| potassium | 포타슘 | 0.15% | **0.00%** | 1.09% |
| di- | 디 | 5.00% | 1.88% | 0.14% |
| di- | 다이 | 5.38% | **0.00%** | 4.49% |
| tri- | 트리 | 2.42% | 1.03% | 0.14% |
| tri- | 트라이 | 1.81% | **0.00%** | 1.74% |

On sodium and potassium the two ingredient registries do not overlap at all: each uses one form exclusively and never the other. KOSHA uses both.

### 4.5 The split is a naming strategy, not four words

Element names turned out to be a symptom. A counter-ion can be rendered two ways in Korean — translated into Sino-Korean, or transliterated from English — and each registry has settled on one.

**Table 5.** Translation against transliteration, by registry.

| English | Korean | Rendering | KOSHA | MFDS drugs | KCIA cosmetics |
|---|---|---|---:|---:|---:|
| sulfate | 황산 | translated | 2.14% | 2.30% | **0.00%** |
| sulfate | 설페이트 | transliterated | 0.19% | 0.30% | 1.52% |
| phosphate | 인산 | translated | 1.93% | 1.21% | **0.00%** |
| phosphate | 포스페이트 | transliterated | 0.37% | 0.30% | 1.38% |
| hydrochloride | 염산 | translated | 0.31% | 14.61% | **0.00%** |
| hydrochloride | 클로라이드 | transliterated | 1.16% | **0.00%** | 0.87% |
| hydrate | 수화물 | translated | 1.36% | 9.09% | **0.00%** |
| hydrate | 하이드레이트 | transliterated | 0.15% | **0.00%** | 0.07% |

The cosmetics column has four zeros and they are all in the translated rows: in 1,380 ingredient names the register never once translates a counter-ion. Pharmacy runs the other way, translating heavily — 염산 appears in 14.6% of drug ingredient names — and never using 클로라이드 or 하이드레이트 at all.

This is why 염화 was mined for *chloride* in Section 4.2. That entry is correct for KOSHA and for pharmacy and wrong for cosmetics, and no amount of care in the mining could have found a form that serves all three, because no such form exists.

It also explains the shape of Table 1. The Korean cosmetics figure sits at 12.5% and the Korean drug figure at 8.1%, both far below the source domain, and for opposite reasons: cosmetics spells things one way the lexicon does not hold, pharmacy spells them the other. KOSHA, sitting between them and using both, is the only registry a single-spelling lexicon could have been mined from without the inconsistency showing up immediately.

Two further causes are specific to each catalogue. Some 45.8% of cosmetic ingredient names are botanical, built from Korean plant names and the words 추출물, 꽃, 잎, 뿌리, which have no Latin root by construction; excluding them raises Korean cosmetics coverage to 20.8%. Drug ingredient names carry salt and hydrate suffixes — 염산염, 나트륨, 수화물 — which the lexicon does not hold and which are grammar rather than vocabulary.

The Korean and English sides locate the limit differently in each. For cosmetics the two agree closely, 12.5% against 15.9%, so what is missing is vocabulary. For drugs the gap is wider, 8.1% against 14.7%, which is the translation strategy showing up as a number: the English side is transliterable and the Korean side has already been translated away from the root.

## 5. Discussion

The source-domain figure of 40.4% is not a ceiling. What remains unexplained is element names (나트륨, 칼륨), trivial names with no compositional structure, and stems that did not clear the mining thresholds. Raising coverage means extending the candidate list, not changing the method.

The INN figure of 8.5% was measured against English roots. Korean transliterations of those radicals as a published list were not obtainable, so that row shows only that the roots themselves recur.

### 5.1 Three registries, one language, three house styles

The result is small to state and awkward to live with. A Korean reader who meets sodium lauryl sulfate on a shampoo bottle, sodium hydroxide on a safety data sheet, and 염산 in a prescription leaflet is given different Korean words for the same chemistry by three public bodies, in one language. None of them is wrong inside its own register. 나트륨 is standard chemical and pharmaceutical Korean, 소듐 is the standard cosmetics transliteration, and every form in Table 5 is officially maintained by someone.

For a sighted reader the cost is a moment's friction, and often not even that, because the packaging carries a shape and a colour and a shelf position that carry the identification instead. For the accessibility case this series argues, none of that is available. Braille and speech deliver the string and nothing else, so the reader has only the word — and someone assembling a list of ingredients to avoid has no way to know that the 소듐 on one label and the 나트륨 on another are one substance.

The engineering consequence is narrow and useful. A lexicon meant to cross registries needs variant spellings recorded as alternates of one root, and it needs to record which registry uses which, because the alternates are not interchangeable within a document. That is a schema decision, and Section 4.5 is the argument for making it before the lexicon is built rather than patching it afterwards.

There is a second consequence for how such a lexicon should be mined. KOSHA looked like the natural source: it is the largest aligned corpus available and it is the domain this series began in. It is also, of the three registries measured, the only one without a consistent house style. Mining from it produced a lexicon that reads as neutral and is in fact a blend, and the blend is invisible until it is measured against a registry that has committed to one convention.

We do not propose that any of the three bodies change its convention. All are settled, they answer to different statutes, and an accessibility project is not the right instrument for standardising a national scientific vocabulary. The asymmetry is worth naming, though: the cost of the divergence falls almost entirely on readers who cannot see the package.

## 6. Limitations

- The lexicon is mined from one regulatory corpus and reflects its transliteration conventions. Section 4.4 measures that limitation rather than removing it: the lexicon still holds one spelling per root.
- The cosmetics figure comes from a 1,380-entry sample, not a census. Sampling was by fixed page stride, which is unbiased with respect to the dictionary's ordering but is still a sample.
- The drug ingredient names were recovered from the parenthetical in the product name, not from a dedicated ingredient field. That favours single-ingredient generics, which are the products that print the ingredient there; combination products and originator brands are under-represented.
- Both ingredient catalogues were swept through search rather than enumerated, so neither is a census and the rates carry sampling error that we have not quantified.
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

Across five readings of three registries the result splits in two. Chemical vocabulary crosses the boundary between them: the same roots name industrial chemicals, drug ingredients and cosmetic ingredients, in both scripts. Orthographic convention does not cross it. On sodium and potassium the pharmaceutical and cosmetic registers do not overlap by a single name, and the divergence is systematic: cosmetics transliterates counter-ions and never translates them, pharmacy translates them and rarely transliterates. A lexicon built for one catalogue under-reads in another for reasons that have nothing to do with chemistry, and the fix is a schema that stores variant spellings per root together with the registry each belongs to.

The pharmaceutical row carries a second lesson, and this version can close it rather than argue it. Measured on product names the lexicon reached 1.5%; measured on ingredient names from the same agency it reaches 8.1%. Failing to check what a public endpoint returns produces a number that reads as failed transfer and is really a failed measurement.

## Reproduction

```
python scripts/mine_morphemes.py                  # rebuilds data/morphology/roots.json
python scripts/fetch_kcia_sample.py               # samples the cosmetics dictionary
python scripts/fetch_mfds_ingredients.py          # drug ingredient names
python scripts/domain_coverage.py                 # rebuilds docs/track-a-coverage-report.md
python scripts/naming_convention_divergence.py    # Tables 3, 4 and 5
```

`fetch_kcia_sample.py` writes to `data/kcia_cache/`, which is gitignored under the dictionary's terms of use. Everything downstream reads statistics, not entries.

`fetch_mfds_ingredients.py` calls the MFDS approval register directly. The key is read from a file outside the repository and no credential is copied into it. Its output is public government data and is committed.

## References

[1] Kim, Y. (2026). KOSHA-Braille: infrastructure-grade accessibility for Korean chemical safety information. *Universal Access in the Information Society*, 25, 116. https://doi.org/10.1007/s10209-026-01381-0

[2] IUPAC. *Nomenclature of Organic Chemistry: Recommendations and Preferred Names*. Royal Society of Chemistry, 2013.

[3] World Health Organization. *International Nonproprietary Names (INN) for Pharmaceutical Substances: Names for Radicals, Groups and Others*. WHO/EMP/RHT/TSN/2015.1.

[4] 대한화장품협회 [Korean Cosmetic Association]. *화장품 성분사전* [Cosmetic Ingredient Dictionary]. https://kcia.or.kr/cid

[5] 대한화학회 [Korean Chemical Society]. *화합물 명명법* [Nomenclature of Chemical Compounds].

[6] 식품의약품안전처 [Ministry of Food and Drug Safety]. 의약품 제품 허가정보 [Drug product approval information], public data set 15095677. https://www.data.go.kr/data/15095677/openapi.do

---

## Figures

**Fig. 1** Reach of the 125-root lexicon by catalogue. Bars give the share of each catalogue's name characters explained by a known root. The pale bar at the bottom is the same agency's product names rather than ingredient names, kept for comparison with the row above it. (`figures/Fig1.png`)

**Fig. 2** The three conditions that decide whether mining works. Each row is a real corpus case: the naive result on the left, the corrected result on the right. (`figures/Fig2.png`)

**Fig. 3** The two halves of the cross-registry result. Left: shared chemical roots occur in all three registries. Right: the same elements and prefixes are spelled one way by pharmacy and the other by cosmetics, with no overlap on sodium or potassium, while KOSHA uses both. Prefixes are counted at name-initial position only. (`figures/Fig3.png`)

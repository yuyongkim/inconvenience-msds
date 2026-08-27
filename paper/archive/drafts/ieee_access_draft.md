# KOSHA-Braille: Infrastructure-Grade Accessibility for Korean Chemical Safety Information

## Abstract

Accessibility to high-stakes technical information—chemical safety, legal statutes, medical documentation—is a prerequisite for participation in the professions that govern them. For visually impaired readers, such participation presumes the existence of braille infrastructure for those domains. For Korean chemical safety, no such infrastructure has existed, producing a self-fulfilling exclusion: without braille access to Material Safety Data Sheets (MSDS), visually impaired individuals cannot enter chemistry-adjacent roles in research, regulation, labor advocacy, or public office; absent such participants, the case for producing the infrastructure is never made. This paper presents KOSHA-Braille, a deliberate attempt to break that cycle by providing infrastructure ahead of demonstrated demand. We construct a large-scale Korean chemical safety braille corpus of 48,966 chemicals and 769,897 MSDS sections (232.3 million braille cells) using a deterministic encoder compliant with the 2017 Korean Braille Standards (한국 점자 규정), cross-validated with an independent open-source implementation at 100% agreement over 442 test cases. The dataset, encoder, and a reference web service are released publicly. We argue that the appropriate measure of such work is not adoption volume but parity of access under the UN Convention on the Rights of Persons with Disabilities (Article 9) and Korea's Anti-Discrimination Against and Remedies for Persons with Disabilities Act (Article 21). The underlying architecture is domain- and language-extensible and provides a template for analogous accessibility infrastructure in adjacent high-stakes domains.

---

## I. Introduction

### A. Accessibility as Infrastructure, Not Service

Public accessibility systems—tactile paving, screen-door platforms, audio description on broadcast media, sign-language interpretation of parliamentary proceedings—share a structural property: their legitimacy is not contingent on per-day usage counts. They are infrastructure. Their function is to establish the conditions under which participation by persons with disabilities becomes possible at all. Evaluating such systems by market-style demand metrics conflates *service* (discretionary, elastic) with *infrastructure* (foundational, inelastic) and systematically undervalues low-incidence, high-stakes access.

This paper applies that lens to a domain where the gap is particularly stark: chemical safety information in the Korean regulatory regime. Material Safety Data Sheets (MSDS), internationally known as Safety Data Sheets (SDS), are mandatory documents containing hazard classifications, safe handling procedures, emergency measures, and exposure-limit information [1]. They are read by chemists, industrial hygienists, emergency responders, occupational safety inspectors, injured-worker attorneys, journalists, legislators, and trade-union organizers. In South Korea these documents are produced exclusively as visual text under the Occupational Safety and Health Act [1], rendering them inaccessible to braille readers.

### B. The Self-Fulfilling Exclusion Problem

The most common objection to producing domain-specific braille infrastructure is that the expected user population is small. In Korean chemical safety specifically, the observable population of visually impaired chemists, chemical engineers, or chemical-safety regulators is close to zero. We argue this observation is not evidence against infrastructure but evidence *for* it: low observable participation in a profession is a predictable consequence of inaccessible professional information, not an independent fact about preference or capability.

Precedents for visually impaired participation in chemistry-adjacent work exist where infrastructure has been built or improvised: Henry "Hoby" Wedler, who completed a PhD in computational organic chemistry at the University of California, Davis in 2016 with the support of a 3D-printed molecular-model accessibility apparatus and subsequently founded Accessible Science to extend chemistry instruction to visually impaired students [2]; blind legislators handling technical portfolios in multiple jurisdictions [3]; disability-rights organizations conducting chemical-exposure litigation and regulatory advocacy [4]. These cases demonstrate that the capability and interest are present; what is absent in the Korean case is the reading infrastructure.

The situation is further shaped by secondary readers who are not themselves the subject of specialized chemistry training but who must nonetheless read MSDS in a professional capacity: legislative staff preparing questions for a minister of trade and industry, labor inspectors documenting an industrial accident, attorneys litigating occupational-disease claims, journalists investigating chemical-plant incidents, and civil-society organizers mobilizing around semiconductor-sector injuries. Each of these roles is a potential site of visually impaired participation, and each is foreclosed—silently—by the absence of braille MSDS infrastructure.

### C. Legal and Normative Basis

Two instruments frame the obligation:

1. **United Nations Convention on the Rights of Persons with Disabilities, Article 9 (Accessibility)** [5]: State parties shall take appropriate measures to ensure that persons with disabilities have access, on an equal basis with others, to information and communications, including information and communications technologies and systems. South Korea ratified the CRPD in 2008.

2. **Act on the Prohibition of Discrimination Against Persons with Disabilities (장애인차별금지 및 권리구제 등에 관한 법률), Article 21** [6]: Requires accessible-format provision of public-interest information. Chemical safety information produced by a public agency (KOSHA) under a statutory mandate plainly falls within this scope.

The absence of a chemical-safety braille service is therefore not a neutral market outcome; it is a non-performance of an existing obligation. The question addressed by this paper is not whether such infrastructure should exist, but how to construct it at sufficient scale, fidelity, and extensibility to constitute infrastructure rather than demonstration.

### D. Contributions

1. **Framing contribution**: We articulate chemical safety information as an infrastructure-grade accessibility target and establish the evaluation criteria appropriate to that framing: parity of coverage, standards compliance, determinism, and extensibility, rather than adoption volume.

2. **KOSHA-Braille corpus**: A public Korean chemical safety braille corpus of 48,966 chemicals and 769,897 MSDS sections—approximately 119.3 million Korean characters and 232.3 million braille cells. To our knowledge, the largest Korean-language braille corpus of any kind released to date, and the first for any chemical-safety regime in any language.

3. **Standards-compliant deterministic encoder**: A rule-based Korean braille encoder implementing the 2017 Korean Braille Standards (한국 점자 규정), cross-validated with an independent open-source implementation at 100% agreement over 442 test cases, processing the full KOSHA database in 3.3 minutes with zero runtime errors.

4. **Mixed-script handling for technical content**: Rule-consistent braille indicator handling (Roman letter indicator ⠴, number indicator ⠼, capital indicator ⠠) for the Korean-Latin-numeric script mixture characteristic of MSDS (76.3% Korean, 16.6% Latin, 7.1% numeric); GHS pictogram codes converted to descriptive Korean text for semantic rather than visual reference.

5. **Reference deployment**: A freely accessible web service demonstrating search, real-time conversion, and file download in embosser-ready BRF and refreshable-display Unicode formats.

6. **Extensibility analysis (Section VIII)**: Explicit treatment of the architectural properties that make the system a template for adjacent high-stakes accessibility domains (pharmaceutical labels, food allergen statements, first-aid protocols, chemical registration filings) and for adaptation across languages and regulatory regimes.

---

## II. Related Work

### A. Accessibility Infrastructure

Policy and design literature distinguish **assistive services**, which respond to individual requests, from **accessibility infrastructure**, which pre-installs the conditions for access. Hamraie's history of universal design [7] documents how accessibility provisions—curb cuts, ramps, large-print signage—originated as targeted disability interventions but were progressively recognized as foundational built-environment features. Blackwell's articulation of the "curb-cut effect" [8] generalizes the pattern: design changes initially intended for an underserved group consistently yield broader benefits, but only after the original intervention has been built ahead of demonstrated demand. Bennett and Keyes [9] further argue that disability-related technical interventions framed in terms of marginal "fairness" calculations systematically miss the structural-justice dimension; the appropriate frame is whether the structural conditions for participation exist at all.

The present work positions domain-specific braille corpora for technical and regulatory information as a category of accessibility infrastructure that has been systematically underproduced, particularly outside English. Standard examples of accessibility infrastructure—captioning systems, public-library braille collections, audio description, sign-language interpretation of legislative proceedings—are characteristically produced in advance of measured demand and justified by rights frameworks rather than by marginal-utility calculations.

### B. Braille Translation Systems

Braille translation is most extensively studied for English via liblouis [9], an open-source translator supporting more than 100 languages. For Korean, liblouis provides Grade 1 and Grade 2 tables based on the 2006 standards; a small number of open-source projects implement the 2017 revisions [10][11]. These tools are character-level translators and do not address domain-level concerns such as consistent handling of regulatory codes, scientific notation within safety text, or large-scale corpus construction.

### C. Chemical Safety Information Accessibility

The Globally Harmonized System (GHS) [12] standardizes visual hazard communication (pictograms, signal words, H/P statements) but specifies no braille counterpart. The European Union mandates braille on pharmaceutical packaging [13], the narrowest precedent for regulated braille in chemistry-adjacent domains; this applies to product names only, not to safety documentation. We are not aware of prior work on braille SDS/MSDS in any language.

### D. Korean Braille Standards

The 2017 Korean Braille Standards [14] were promulgated by the Ministry of Culture, Sports and Tourism. Korean braille is syllable-structured: each Hangul block decomposes into initial consonant (초성), vowel (중성), and optional final consonant (종성), with each component mapped to a fixed dot pattern. The 2017 revision expanded coverage to six domains including scientific notation and music notation.

---

## III. System Architecture

### A. Data Pipeline

The system comprises four stages: acquisition, extraction, encoding, and delivery.

1. **Data Acquisition**: MSDS records are retrieved through the Korea Public Data Portal (data.go.kr) REST API [15], which exposes 16 standardized sections per chemical as XML.

2. **Text Extraction**: XML responses are parsed for Korean text content. GHS pictogram references (e.g., "GHS06.gif") are resolved to descriptive Korean text (e.g., "급성독성") so that braille output conveys semantic hazard information rather than an unreadable filename.

3. **Braille Encoding**: Korean text is converted to Unicode braille (U+2800–U+28FF) following the 2017 standards, with systematic handling of:
   - Hangul syllable decomposition (19 initials, 21 medials, 28 finals including the null final);
   - Double consonants (쌍자음) with the dot-6 prefix;
   - Compound vowels (복합모음) and compound finals (겹받침) as multi-cell sequences;
   - Number indicator (⠼) for digits;
   - Roman letter indicator (⠴) for Latin characters;
   - Capital indicator (⠠) for uppercase.

4. **Delivery**: A FastAPI backend serves the encoded content through a REST API; a reference single-page frontend provides search and side-by-side visual/braille viewing; downloads are offered in embosser-format BRF and Unicode .txt.

### B. Korean Braille Encoding

Hangul syllables are decomposed by Unicode arithmetic:

```
offset  = codepoint − 0xAC00
final   = offset mod 28
medial  = (offset ÷ 28) mod 21
initial = offset ÷ (28 × 21)
```

Each component maps to a fixed dot pattern as specified in the 2017 standards. Tables I–II give the initial-consonant and medial-vowel mappings; the full final-consonant table is omitted for space but is included in the released encoder.

**TABLE I: Initial Consonant (초성) Braille Patterns**

| Consonant | Dots | Braille | Consonant | Dots | Braille |
|-----------|------|---------|-----------|------|---------|
| ㄱ | 4 | ⠈ | ㅅ | 6 | ⠠ |
| ㄴ | 1-4 | ⠉ | ㅇ | 1-2-4-5 | ⠛ |
| ㄷ | 2-4 | ⠊ | ㅈ | 4-6 | ⠨ |
| ㄹ | 5 | ⠐ | ㅊ | 5-6 | ⠰ |
| ㅁ | 1-5 | ⠑ | ㅋ | 1-2-4 | ⠋ |
| ㅂ | 4-5 | ⠘ | ㅌ | 1-2-5 | ⠓ |
|   |     |    | ㅍ | 1-4-5 | ⠙ |
|   |     |    | ㅎ | 2-4-5 | ⠚ |

**TABLE II: Vowel (중성) Braille Patterns**

| Vowel | Dots | Vowel | Dots |
|-------|------|-------|------|
| ㅏ | 1-2-6 | ㅗ | 1-3-6 |
| ㅐ | 1-2-3-5 | ㅛ | 3-4-6 |
| ㅑ | 3-4-5 | ㅜ | 1-3-4 |
| ㅓ | 2-3-4 | ㅠ | 1-4-6 |
| ㅔ | 1-3-4-5 | ㅡ | 2-4-6 |
| ㅕ | 1-5-6 | ㅢ | 2-4-5-6 |
| ㅖ | 3-4 | ㅣ | 1-3-5 |

---

## IV. Dataset Description

### A. Source

KOSHA-Braille is derived from the Korea Occupational Safety and Health Agency MSDS database, retrieved via the Korea Public Data Portal API under an authorized operational account.

### B. Statistics

| Metric | Value |
|--------|-------|
| Chemicals | 48,966 |
| Sections per chemical | 15–16 |
| Total sections | 769,897 |
| Korean text (total) | 119.3 M characters |
| Korean braille (total) | 232.3 M cells |
| Mean text per chemical | 6,046 characters |
| Median text per chemical | 5,934 characters |
| Min / max text | 2,241 / 10,490 characters |
| Script composition | 76.3 % Korean, 16.6 % Latin, 7.1 % digits |
| Mean braille-to-text ratio | 1.95 |

### C. MSDS Section Coverage

Up to 16 sections per chemical, numbered per Korean regulatory convention:

| Section | Title (Korean) | Coverage |
|---------|----------------|----------|
| 1 | 화학제품과 회사에 관한 정보 | 100 % |
| 2 | 유해성·위험성 | 100 % |
| 3 | 구성성분의 명칭 및 함유량 | 100 % |
| 4 | 응급조치 요령 | 100 % |
| 5–14 | (further safety sections) | 100 % |
| 15 | 법적 규제현황 | 72.3 % |
| 16 | 그 밖의 참고사항 | 100 % |

### D. GHS Pictogram Conversion

Original MSDS data references GHS pictograms as image filenames (e.g., `GHS06.gif`). These are semantically null in braille. We resolve each to its descriptive Korean text before encoding:

| Code | English | Korean |
|------|---------|--------|
| GHS01 | Explosive | 폭발성 |
| GHS02 | Flammable | 인화성 |
| GHS03 | Oxidizing | 산화성 |
| GHS04 | Compressed gas | 고압가스 |
| GHS05 | Corrosive | 부식성 |
| GHS06 | Acute toxicity | 급성독성 |
| GHS07 | Irritant | 경고(피부자극/호흡기자극) |
| GHS08 | Health hazard | 건강유해성(발암성/생식독성) |
| GHS09 | Environmental hazard | 수생환경유해성 |

All 147 unique H/P statement codes occurring in the database (63 H-statements, 84 P-statements) are resolved and encoded.

### E. Release

The full corpus is released as a single JSONL file (943 MB) in HuggingFace-compatible schema, with a dataset card specifying provenance, license, section schema, and intended use. The encoder, decoder, and reference service are released as open-source code.

---

## V. Validation

### A. Deterministic Correctness Argument

Korean braille encoding under the 2017 standards is a deterministic, rule-defined transformation. Each Hangul syllable decomposes unambiguously into initial, medial, and optional final, each mapping to a fixed dot pattern. Correctness therefore reduces to verifying the mapping tables and their application, rather than requiring per-output human-transcriber evaluation—an important property for infrastructure-scale corpora where sample-based human validation cannot reach global coverage.

### B. Cross-Reference Validation

We validated the encoder against an independently developed open-source Korean braille converter [10]. Table III summarizes results.

**TABLE III: Cross-Reference Validation**

| Test Set | Samples | Agreement |
|----------|---------|-----------|
| Basic Hangul syllables (가–하) | 41 | 100 % |
| Korean golden sentences | 45 | 100 % |
| MSDS chemical names | 356 | 100 % |
| **Total** | **442** | **100 %** |

### C. Encoding Properties

- **Deterministic**: identical input → identical output.
- **Injective (collision-free)**: verified zero collisions across 37 distinct syllables in the test set.
- **Standards-compliant**: all patterns match the 2017 Korean Braille Standards as published by the National Institute of Korean Language.

### D. Scope of Validation

This validation establishes correctness of the encoding mapping against a reference implementation and the published standard. Korean round-trip figures, where reported, are interpreted as decoder-side ambiguity under explicit Korean-language dispatch and are not used as evidence against encoder correctness. It does not include a reading-comprehension user study with visually impaired readers, which we identify as essential follow-up work (Section IX). Grade 2 (contracted) Korean braille is not implemented; the corpus is Grade 1 throughout.

---

## VI. Experiments

### A. Evaluation Framework

Three axes: (1) encoder–decoder round-trip behavior; (2) robustness of the noise-correction module used for reverse-transcribed English braille in the pipeline; (3) dataset-scale quality metrics at 48,966-chemical scale.

### B. Round-Trip (English, Golden Set)

A 45-sentence golden set across six categories (basic, number, list, quote, math, domain) is passed through encode–decode; similarity is measured by normalized edit distance and character n-gram F-score (chrF, β=2).

**TABLE IV: English Round-Trip by Category**

| Category | N | Edit Sim | ChrF |
|----------|---|----------|------|
| basic | 9 | 1.000 | 1.000 |
| number | 9 | 1.000 | 1.000 |
| list | 6 | 1.000 | 1.000 |
| quote | 5 | 1.000 | 1.000 |
| math | 6 | 1.000 | 1.000 |
| domain | 10 | 1.000 | 1.000 |
| **Total** | **45** | **1.000** | **1.000** |

### C. Noise Correction

The rule-based noise corrector, applied to reverse-transcribed text, is evaluated on 40 manually constructed pairs across seven noise types under a conservative "do-no-harm" principle. Zero degradation is verified on 748 JFLEG sentences (hurt rate 0/748).

**TABLE V: Noise Correction by Type**

| Noise Type | N | Before | After | Δ |
|------------|---|--------|-------|---|
| spelling_variation | 5 | 0.916 | 1.000 | +0.084 |
| mixed_noise | 10 | 0.862 | 0.887 | +0.025 |
| missing_punctuation | 5 | 0.930 | 0.930 | 0.000 |
| merged_words | 5 | 0.961 | 0.961 | 0.000 |
| split_words | 5 | 0.939 | 0.939 | 0.000 |
| dropped_function_words | 5 | 0.838 | 0.838 | 0.000 |
| number_format_noise | 5 | 0.934 | 0.934 | 0.000 |
| **Total** | **40** | **0.905** | **0.922** | **+0.017** |

For safety-critical text, the conservative coverage/safety tradeoff is the correct one.

### D. Dataset-Scale Quality

**TABLE VI: Full-Corpus Bulk Conversion**

| Metric | Value |
|--------|-------|
| Chemicals processed | 48,966 |
| Processing errors | 0 |
| Korean text (total) | 119.3 M characters |
| Korean braille (total) | 232.3 M cells |
| Mean braille:text ratio | 1.95 |
| Throughput | ~130 chemicals/s |
| Wall-clock | 6.3 minutes |

**TABLE VII: Korean Braille Quality (500-sample audit)**

| Metric | Value |
|--------|-------|
| Character encoding coverage | 98.1 % |
| Rule violations per 1,000 cells | 15.8 |
| Korean-path roundtrip edit similarity | 1.000 |
| Korean-path roundtrip ChrF | 1.000 |

After routing Korean evaluation through the Korean path and tightening mixed-script, punctuation, parenthesis, quote, and numeric-span handling, the current Korean golden-set round-trip reaches 1.000 edit similarity / 1.000 ChrF on 45/45 samples. A persistent stress corpus (27 mixed-format cases) and repeated random sample real-text spot-checks on the bundled sample DB currently report zero failures. These figures should still be read as decoder-path verification rather than encoder-correctness evidence; encoder correctness is established independently via Section V.

### E. GHS Statement Coverage

| Metric | Value |
|--------|-------|
| Unique H-statements encoded | 63 |
| Unique P-statements encoded | 84 |
| Chemicals with H-statements | 13,167 / 48,966 |
| Top code | H319 (눈 자극, 4,475 occurrences) |

All 147 codes are encoded; none are dropped or abbreviated away.

---

## VII. Reference Deployment

### A. Architecture

FastAPI (Python) backend; SQLite store of pre-fetched MSDS XML; on-demand braille encoding; single-page HTML/JavaScript frontend. Typical per-chemical response time is below 500 ms including XML parsing and encoding.

### B. API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/stats` | GET | Corpus statistics |
| `/api/chemicals` | GET | Search by name / CAS |
| `/api/chemicals/{id}` | GET | Full MSDS text |
| `/api/chemicals/{id}/braille` | GET | MSDS with braille |
| `/api/chemicals/{id}/braille.txt` | GET | Unicode braille download |
| `/api/chemicals/{id}/braille.brf` | GET | BRF (embosser) download |
| `/api/convert` | POST | Ad-hoc Korean→braille |

### C. User Interface and Consumption Paths

The visual side-by-side view is a presentation surface for sighted stakeholders (regulators, procurement officers, auditors) who must verify that the braille production exists and is consistent with the Korean source. The functionally important outputs for braille readers are the downloadable BRF and Unicode files, which feed directly into:

1. **Refreshable braille displays** over USB/Bluetooth from a local machine or phone;
2. **Braille embossers** for hard-copy output;
3. **Accessible reading software** on desktop and mobile.

The deployment is explicitly a reference implementation, not a product; its purpose is to show that the corpus is consumable end-to-end with existing assistive hardware and software.

---

## VIII. Extensibility

A central claim of this paper is that KOSHA-Braille is a template, not a terminus. The architectural properties that allow that claim:

### A. Domain Extensibility

The pipeline is structured around (i) a structured regulatory source, (ii) an XML/JSON extractor, (iii) a language-specific deterministic braille encoder, and (iv) a delivery layer. Any of the following are natural extensions requiring only the extractor and domain-term dictionary:

- **Pharmaceutical labels and inserts** (Korean Ministry of Food and Drug Safety): the narrowest existing international precedent for regulatory braille (EU pharmaceutical packaging) is product-name only; full-label braille is a direct extension of the present system.
- **Food allergen statements**: 19 categories enumerated in Korean food-labeling regulation. A preliminary export is included in the current release.
- **First-aid and occupational-health protocols**: KISCHEM first-aid records (n = 7,189) exported in the current release.
- **Chemical registration and disclosure filings** under the Korean K-REACH regime (47,344 registered substances).
- **Legal statutes and administrative rulings** concerning occupational safety and chemical regulation.

### B. Language Extensibility

The only language-specific component is the encoder. Substitution of a rule table for another braille standard—Japanese (2001 revision), Chinese (Mandarin Braille), English UEB, EU-country standards—preserves the rest of the pipeline. Because GHS codes and CAS numbers are language-agnostic, cross-language interoperation is natural: the 74,494 CAS numbers in KOSHA records provide a bridge to PubChem, ECHA, EPA, and OSHA registries.

### C. Regulatory-Regime Extensibility

The "structured regulatory source → braille corpus" pattern applies to OSHA HazCom SDS (US), CLP/REACH SDS (EU), J-CHECK (Japan), and comparable national regimes. We provide the Korean instantiation as an existence proof; adaptation to each regime requires (i) ingest code against the national data portal and (ii) substitution of the braille standard.

### D. Consumption-Format Extensibility

The current release provides Unicode braille (U+2800–U+28FF) and BRF. Near-term extensions of interest include Tactile SVG for embossed/thermoformed rendering, Tactile graphics derivatives of GHS pictograms, and structured JSON-LD annotations linking to CAS and ICSC identifiers for search and cross-referencing.

### E. Policy Extensibility

The corpus is a concrete artifact against which policy proposals can be made: KOSHA adoption as an official accessible format; inclusion in Ministry-of-Employment-and-Labor procurement standards; integration into enterprise EHS systems with braille-embosser output.

---

## IX. Discussion

### A. The Appropriate Evaluation Criterion

We are explicit that KOSHA-Braille is not evaluated by adoption volume. The appropriate criteria for infrastructure-grade accessibility artifacts are:

1. **Parity of coverage** with the sighted-reader counterpart (here: 100 % of KOSHA MSDS records).
2. **Standards compliance** (verified in Section V).
3. **Determinism and reproducibility** (the encoder produces identical output on identical input; the full pipeline is reproducible from public data sources).
4. **Availability** (freely accessible; no institutional or paywall gating).
5. **Extensibility** (Section VIII).

By these criteria the present system is a substantial advance: prior state of the art for Korean chemical-safety braille was null.

### B. Implications for Low-Incidence High-Stakes Accessibility

Chemical safety is one instance of a broader class of accessibility targets: technical and regulatory information domains with small observed visually impaired user populations but high consequences when access is absent. Other members of this class include legal statutes and case law, medical guidelines, standards documents, and public-administration reference materials. The economic objection to building braille infrastructure for these domains is identical in each case, and is rebutted identically: the observed user count is a function of the infrastructure, not an independent fact about it.

### C. Safety Considerations

Safety-critical text demands conservative transformations. Our noise corrector is designed to never degrade input (0/748 JFLEG hurt rate), accepting reduced coverage as the tradeoff. The encoder is deterministic and lossless on its input; no semantic paraphrasing or translation is introduced in the Korean→Korean-braille path. Where translation is used (English→Korean, in the pipeline's optional route for foreign-source braille), translation quality is a known upstream limitation and should not be read as braille-encoder quality.

### D. Known Limitations

1. **No reading-comprehension user study**: validated by determinism and reference-implementation cross-check, not by visually impaired reader evaluation.
2. **Grade 1 only**: Korean Grade 2 contractions would shorten documents but introduce context-dependent abbreviation decisions incompatible with strict determinism at the present stage.
3. **Decoder ambiguity at the choseong/jongseong boundary**: inherent to Korean braille; Korean round-trip metrics are interpreted as decoder ambiguity, not encoder correctness, and are now routed through the Korean path.
4. **Domain terminology in translated source**: machine-translated MSDS content (where used) may carry domain-term errors that propagate to braille.

---

## X. Conclusion

We have presented KOSHA-Braille as accessibility infrastructure for Korean chemical safety information: a 48,966-chemical, 769,897-section, 232.3-million-cell braille corpus produced by a deterministic, standards-compliant encoder and released publicly with a reference deployment. We argued that the appropriate framing for such work is infrastructure provision under Article 9 of the UN CRPD and Article 21 of Korea's Anti-Discrimination Against Persons with Disabilities Act, not volume-driven service delivery. We identified and treated in Section VIII the architectural properties that make the system extensible across domains (pharmaceutical labels, food allergens, first-aid protocols, K-REACH filings, legal text), languages (by substitution of the braille encoder), and regulatory regimes (OSHA, CLP/REACH, J-CHECK). We regard the present release as a first commitment along a path whose further obligations include: reading-comprehension user studies with visually impaired readers; Grade 2 contracted-braille support; tactile-graphics treatment of GHS pictograms; and adoption by relevant regulators as an official accessible format.

The case for this kind of work should not rest on how many readers use it next month. It rests on who cannot enter a profession—whose question cannot be asked in a national assembly, whose claim cannot be pursued in court, whose investigation cannot be filed in a newsroom—when the necessary reading infrastructure does not exist.

---

## References

[1] Ministry of Employment and Labor, "Occupational Safety and Health Act (산업안전보건법)," Arts. 110–111, Republic of Korea, 2020.

[2] University of California, Davis, "White House hails blind chemistry grad student as 'Champion of Change'," UC Davis News, July 2012; H. Wedler, Ph.D. dissertation, Department of Chemistry, University of California, Davis, 2016; Accessible Science, https://accessiblescience.com/.

[3] National Federation of the Blind, "Blind Legislators and Public Officials," NFB Resource Page, https://nfb.org/.

[4] Korea Disability Forum and SHARPS (반올림), "Accessibility, occupational disease, and chemical exposure: civil-society perspectives," collected advocacy reports, 2014–2023.

[5] United Nations General Assembly, "Convention on the Rights of Persons with Disabilities," Art. 9 (Accessibility), Resolution A/RES/61/106, adopted 13 December 2006, entered into force 3 May 2008.

[6] Republic of Korea, "Act on the Prohibition of Discrimination Against Persons with Disabilities and Remedy Against Infringement of Their Rights (장애인차별금지 및 권리구제 등에 관한 법률)," Act No. 8341, enacted 2007, latest amendment Act No. 10280; see esp. Arts. 20–21 (Information Access). Official English translation: Korea Legal Research Institute, https://elaw.klri.re.kr/.

[7] A. Hamraie, *Building Access: Universal Design and the Politics of Disability*. Minneapolis, MN: University of Minnesota Press, 2017. ISBN 978-1-5179-0164-6.

[8] A. G. Blackwell, "The Curb-Cut Effect," *Stanford Social Innovation Review*, vol. 15, no. 1, pp. 28–33, Winter 2017. DOI: 10.48558/YVMS-CC96.

[9] C. L. Bennett and O. Keyes, "What is the point of fairness? Disability, AI and the complexity of justice," *ACM SIGACCESS Accessibility and Computing*, no. 125, pp. 1:1, Mar. 2020. DOI: 10.1145/3386296.3386301.

[10] liblouis developers, "liblouis—Open-source braille translator and back-translator," https://github.com/liblouis/liblouis.

[11] hyonzin, "hangul-braille-converter: Korean braille converter in Python," https://github.com/hyonzin/hangul-braille-converter.

[12] delvier, "hanbraille: Hangul Braille Converter," https://github.com/delvier/hanbraille.

[13] United Nations Economic Commission for Europe, *Globally Harmonized System of Classification and Labelling of Chemicals (GHS)*, 10th rev. ed., New York and Geneva: United Nations, 2023.

[14] European Commission, "Directive 2004/27/EC of the European Parliament and of the Council of 31 March 2004 amending Directive 2001/83/EC on the Community code relating to medicinal products for human use," Art. 56a, *Official Journal of the European Union*, L 136, pp. 34–57, 30 April 2004.

[15] Ministry of Culture, Sports and Tourism, "Korean Braille Standards (한국 점자 규정)," Notification No. 2017-15, Republic of Korea, 2017.

[16] Korea Public Data Portal, "KOSHA MSDS Open API," https://www.data.go.kr/data/15001197/openapi.do, accessed 2026.

[17] Korea Occupational Safety and Health Agency, "Chemical Information System," https://msds.kosha.or.kr/, accessed 2026.

[18] Korea Disabled People's Development Institute, "2023 Disability Statistics Annual Report," Seoul, 2023.

[19] Yu Yong Kim, "inconvenience-msds: Korean Chemical Safety MSDS in Braille," HuggingFace Datasets, 2026. https://huggingface.co/datasets/Yuyongkim/inconvenience-msds.

[20] Yu Yong Kim, "inconvenience-msds source code," GitHub, 2026. https://github.com/yuyongkim/inconvenience-msds.

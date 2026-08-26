# Submission package — paper3 → UAIS

**Title.** What Korean Chemical Names Are Made Of: A Mined Transliteration Lexicon and the Registry Conventions It Cannot Cross

**Author.** Yuyong Kim, University of Wisconsin-Madison, Madison, WI 53706, USA
**Email.** ykim288@wisc.edu
**ORCID.** 0009-0006-4842-666X

## Files in this folder

| File | Upload as |
|---|---|
| `manuscript.docx` | Manuscript |
| `cover_letter.docx` | Cover letter |
| `figures/Fig1.png` | Figure 1 (screen) |
| `figures/Fig1.pdf` | Figure 1 (vector) |
| `figures/Fig2.png` | Figure 2 (screen) |
| `figures/Fig2.pdf` | Figure 2 (vector) |
| `figures/Fig3.png` | Figure 3 (screen) |
| `figures/Fig3.pdf` | Figure 3 (vector) |

Figures: 3. Tables: 5, kept inside the manuscript.

## Where it goes

*Universal Access in the Information Society* submits through SNAPP, the
Springer Nature Article Processing Platform, not Editorial Manager. The
first paper in this series went the same way.

  https://submission.nature.com/new-submission/10209

Article type: **Brief Report** (matching the first paper in the series).

## Paste-in metadata

The form asks for these separately from the file. They are reproduced here
so the submitted metadata matches the manuscript rather than being retyped.

### Abstract

**Purpose.** Korean chemical names are transliterations of Latin- and Greek-derived English ones. If the same roots recur in pharmaceutical, cosmetic and pesticide names, one accessibility resource can be extended across regulatory catalogues; if not, each catalogue needs its own vocabulary work. This report presents a root lexicon and a measurement method for answering that question.

**Methods.** Rather than deriving the lexicon from naming rules, we mined it statistically from 8,071 aligned Korean/English name pairs in the KOSHA database. Candidate morphemes were taken from IUPAC nomenclature. For each candidate we compared Korean substring frequencies between the names containing it and those not, and kept the correspondences that separated the two sets. Coverage of the resulting lexicon was then measured over five domains across three Korean regulatory registries, using catalogues that give Korean and English names for the same substance and so separate vocabulary transfer from spelling transfer: 1,380 entries from the cosmetic ingredient dictionary and 1,650 drug ingredient names from the MFDS approval register.

**Results.** The method yields 125 roots. Across 9,903 KOSHA chemical names, 40.4% of the Hangul is accounted for by a known root. Cosmetic ingredient names reach 12.5% on the Korean side and 15.9% on the English; drug ingredient names reach 8.1% and 14.7%. The roots themselves transfer, occurring in all three registries at comparable rates. The spellings do not, and the divergence is systematic rather than incidental. Pharmacy and cosmetics do not overlap at all on the elements sodium and potassium: drugs write 나트륨 and 칼륨, cosmetics write 소듐 and 포타슘, and each form is absent from the other register. The same split runs deeper than element names. Cosmetics transliterates counter-ions (설페이트, 포스페이트) and never translates them; pharmacy translates them into Sino-Korean (황산, 염산, 수화물) and rarely transliterates. KOSHA, the registry this lexicon was mined from, is the only one of the three that uses both.

**Conclusions.** Cross-registry transfer succeeds and fails in different places, and the distinction is the result: chemical vocabulary is shared, orthographic convention belongs to whichever body maintains the register. A lexicon mined in one catalogue under-reads in another for reasons that are administrative rather than chemical, and a Korean reader meets two official spellings of the same substance depending on which label is in their hand. The pharmaceutical figure also settles a question the earlier version of this work could only diagnose: measured on product names the same lexicon reached 1.5%, and measured on ingredient names from the same agency it reaches 8.1%, so the low figure was a failure of measurement rather than of transfer.

### Keywords

transliteration lexicon; morphological decomposition; chemical nomenclature; regulatory data; accessibility infrastructure; domain extension; orthographic convention

## Declarations the form will ask for

- **Funding.** None.
- **Competing interests.** None.
- **Ethics approval.** Not applicable; no human participants or animals.
- **Consent.** Not applicable.
- **Data availability.** The mined lexicon, the measurement scripts and the derived statistics are in the repository. Two sources are described rather than redistributed: the cosmetics dictionary, whose terms reserve copyright to the association, and the drug register, which is read through a service holding the authorised key.
- **Code availability.** Same repository; every figure and table has a named
  script listed under Reproduction.

## Before uploading

- [ ] Open `manuscript.docx` and check the figures are embedded and legible
- [ ] Confirm the abstract above matches the one in the manuscript
- [ ] Confirm the reference to the first paper carries the right DOI
- [ ] Suggested reviewers are at the end of the cover letter

Regenerate this folder with:

```
python scripts/build_submission.py paper3
```

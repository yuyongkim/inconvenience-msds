# Submission package — paper5 → UAIS

**Title.** Person-Independent Evaluation for Korean Fingerspelling Recognition, and Why the Split Is the Result

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

Figures: 2. Tables: 2, kept inside the manuscript.

## Where it goes

*Universal Access in the Information Society* submits through SNAPP, the
Springer Nature Article Processing Platform, not Editorial Manager. The
first paper in this series went the same way.

  https://submission.nature.com/new-submission/10209

Article type: **Brief Report**, as declared in the cover letter.

## Paste-in metadata

The form asks for these separately from the file. They are reproduced here
so the submitted metadata matches the manuscript rather than being retyped.

### Abstract

**Purpose.** Technical terms such as chemical names have no registered sign, so Korean Sign Language spells them with 지문자, one static hand shape per jamo. This report presents an evaluation protocol for static fingerspelling recognition and shows quantitatively that person-independent splitting is not optional.

**Methods.** We classify the 21 hand landmarks MediaPipe produces rather than raw pixels. We define a normalisation that removes position, scale and in-plane rotation from the landmarks, and implement a nearest-centroid classifier with one centroid per jamo. The evaluation harness groups folds by signer and computes the random split alongside for comparison. We also audited the column names of nine public sign-alphabet datasets to see whether they record who signed each sample.

**Results.** On synthetic keypoints carrying a per-signer hand-shape bias, the random split reported accuracy 4.2 points higher than the person-independent split on identical data (0.949 against 0.908). That gap is a floor, because the synthetic bias is more uniform than variation between real hands. Of the seven public datasets whose schema resolved, none carries a signer, subject or participant column.

**Conclusions.** No Korean fingerspelling dataset was obtainable, so **recognition accuracy was not measured.** Every figure reported here is synthetic and demonstrates only that the harness runs and how large the split effect is. The contribution is the evaluation protocol and the evidence for needing it, not a recogniser. Because the public datasets omit signer identity, a person-independent split is not expressible on them at all, which is the practical reason the protocol keeps going unapplied.

### Keywords

Korean Sign Language; fingerspelling; person-independent evaluation; MediaPipe; accessibility; evaluation methodology

## Declarations the form will ask for

- **Funding.** None.
- **Competing interests.** None.
- **Ethics approval.** Not applicable; no human participants or animals.
- **Consent.** Not applicable.
- **Data availability.** The evaluation harness, the synthetic keypoint generator, the public-dataset audit and its raw output are in the repository. No Korean fingerspelling data were collected, so none can be released.
- **Code availability.** Same repository; every figure and table has a named
  script listed under Reproduction.

## Before uploading

- [ ] Open `manuscript.docx` and check the figures are embedded and legible
- [ ] Confirm the abstract above matches the one in the manuscript
- [ ] Confirm the reference to the first paper carries the right DOI
- [ ] Suggested reviewers are at the end of the cover letter

Regenerate this folder with:

```
python scripts/build_submission.py paper5
```

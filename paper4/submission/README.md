# Submission package — paper4 → UAIS

**Title.** Reading a Cosmetics Label Without Aiming: Open Fiducial Markers and Structured Ingredient Summaries Where Braille Does Not Fit

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

Figures: 3. Tables: 4, kept inside the manuscript.

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

**Purpose.** Cosmetics packaging offers no page for braille. A 30 mL bottle can carry a product name and little else, while the ingredient list — the part a user with a fragrance allergy needs — is the longest text on the label. This report presents an alternative route for the boundary case where braille does not extend.

**Methods.** Two components. First, code recognition that does not require aiming: we surveyed the licensing terms of NaviLens and measured detection of the open alternative, ArUco fiducial markers, over a grid of marker size and off-axis angle. Second, an ingredient summariser that restructures an INCI list along concentration order, EU-labelled fragrance allergens, and root decomposition, emitting plain text suited to a speech synthesiser. Because Korean-market labels print Korean ingredient names, we checked the summariser's Korean allergen spellings one by one against the Korean Cosmetic Association dictionary, the body that sets them.

**Results.** On a flat surface, ArUco detection was complete out to 70° off-axis whenever the marker occupied 3.4% of frame width (44 px in a 1280-wide frame). Wrapping the marker onto a cylinder narrowed angle tolerance sharply: at a marker spanning 20% of the container circumference — a serum bottle — tolerance fell to 15°, and at 40% — a lip balm — the marker was read only head-on. Adding a specular highlight, which is what a glossy container gives, left detection intact up to a highlight peak of 130 out of 255 in every condition and broke it in all of them by 210.

**Conclusions.** A non-aim recognition route exists without a commercial licence, but it is less forgiving than the planar measurement suggests. The design constraints are package area **and container curvature**: the tighter the curve, the closer to square on the user must hold the camera. Non-aim reading holds on wide containers and does not hold on narrow ones. The pipeline reports what the label states and what labelling rules single out; it does not assess safety.

### Keywords

accessibility; blindness; non-aim scanning; fiducial markers; cosmetic ingredients; speech output

## Declarations the form will ask for

- **Funding.** None.
- **Competing interests.** None.
- **Ethics approval.** Not applicable; no human participants or animals.
- **Consent.** Not applicable.
- **Data availability.** The marker measurement scripts, the cylinder and specular sweeps, the ingredient summariser and the allergen check are in the repository, together with the printable marker sheet. No photographs exist to release; every detection figure is synthetic and the code that generates it is included.
- **Code availability.** Same repository; every figure and table has a named
  script listed under Reproduction.

## Before uploading

- [ ] Open `manuscript.docx` and check the figures are embedded and legible
- [ ] Confirm the abstract above matches the one in the manuscript
- [ ] Confirm the reference to the first paper carries the right DOI
- [ ] Suggested reviewers are at the end of the cover letter

Regenerate this folder with:

```
python scripts/build_submission.py paper4
```

# Reading a Cosmetics Label Without Aiming: Open Fiducial Markers and Structured Ingredient Summaries Where Braille Does Not Fit

Yuyong Kim
University of Wisconsin-Madison, Madison, WI 53706, USA
Email: ykim288@wisc.edu
ORCID: 0009-0006-4842-666X

---

## Abstract

**Purpose.** Cosmetics packaging offers no page for braille. A 30 mL bottle can carry a product name and little else, while the ingredient list — the part a user with a fragrance allergy needs — is the longest text on the label. This report presents an alternative route for the boundary case where braille does not extend.

**Methods.** Two components. First, code recognition that does not require aiming: we surveyed the licensing terms of NaviLens and measured detection of the open alternative, ArUco fiducial markers, over a grid of marker size and off-axis angle. Second, an ingredient summariser that restructures an INCI list along concentration order, EU-labelled fragrance allergens, and root decomposition, emitting plain text suited to a speech synthesiser.

**Results.** On a flat surface, ArUco detection was complete out to 70° off-axis whenever the marker occupied 3.4% of frame width (44 px in a 1280-wide frame). Wrapping the marker onto a cylinder narrowed angle tolerance sharply: at a marker spanning 20% of the container circumference — a serum bottle — tolerance fell to 15°, and at 40% — a lip balm — the marker was read only head-on.

**Conclusions.** A non-aim recognition route exists without a commercial licence, but it is less forgiving than the planar measurement suggests. The design constraints are package area **and container curvature**: the tighter the curve, the closer to square on the user must hold the camera. Non-aim reading holds on wide containers and does not hold on narrow ones. The pipeline reports what the label states and what labelling rules single out; it does not assess safety.

**Keywords:** accessibility; blindness; non-aim scanning; fiducial markers; cosmetic ingredients; speech output

---

## 1. Introduction

The MSDS braille corpus released earlier in this series [1] assumes a page. Cosmetics packaging has none.

This is the boundary case of the series: a domain where the earlier approach does not extend and the access route itself must change shape. Find the package, identify it without sight, hear the contents.

### 1.1 Why QR is not the answer

A QR code requires framing: a known location, roughly square on, close enough, held still. All four are sighted preconditions. Finding the code is itself the task, and the code offers no help in finding itself.

This is why QR on packaging has never worked for blind shoppers, and it needs stating because QR keeps being proposed as an accessibility solution.

NaviLens exists because of this gap and has been deployed (MTA New York, museums, the Kellogg's Coco Pops trial in the UK). Intellectual property and licensing sit with its parent company Neosistec, and publishing codes requires a per-deployment licence. No public pricing exists.

## 2. Methods

### 2.1 Selecting an open alternative

Open scanners such as ZXing, ZBar and html5-qrcode read QR and barcodes but do not provide the non-aim property. They inherit QR's framing requirement, so nothing changes from the user's side.

The open technology that does have the property is the fiducial marker. ArUco, bundled with OpenCV, and AprilTag were designed for robot pose estimation, where the camera moves and the marker is wherever it happens to be, so detection at distance and angle is the design goal rather than an addition.

### 2.2 Measuring detection

We measured rather than asserted. A marker from the `DICT_4X4_50` dictionary was rendered, warped in perspective about the vertical axis to simulate off-axis viewing, degraded with Gaussian blur (σ = 0.8) and sensor noise (σ = 6), and placed at the centre of a 1280×720 frame. Twelve noise seeds were used per condition.

### 2.3 Summarising the ingredient list

Read verbatim, an INCI list is a run of syllables with no structure. The summariser restructures it along three axes.

**Concentration order.** INCI is ordered by descending concentration, so position carries information that a flat reading discards. The summariser bands the list and reads the head separately.

**Labelled fragrance allergens.** EU Cosmetics Regulation 1223/2009 Annex III requires 26 fragrance allergens to be named on the label above a threshold. The summariser reports those present, in English and Korean transliteration.

The wording matters. The output states that these are ingredients labelling rules require to be named, and that this does not mean they are dangerous. An allergen list read in a warning tone would be a safety claim we are not qualified to make.

**Root decomposition.** Ingredient names are decomposed using the chemical root lexicon of [2]. The Latin and Greek stock that names industrial chemicals also names cosmetic ingredients, which is where the two studies connect. Where the label is in English, the English side of the same lexicon is used.

Output is plain text without markup and passes unchanged through the published braille encoder [1] for a refreshable display.

## 3. Results

**Table 1.** ArUco detection rate. Twelve trials per condition, 1280×720 frame.

| Marker size | 0° | 15° | 30° | 45° | 60° | 70° |
|---:|---:|---:|---:|---:|---:|---:|
| 200 px (15.6%) | 100% | 100% | 100% | 100% | 100% | 100% |
| 120 px (9.4%) | 100% | 100% | 100% | 100% | 100% | 100% |
| 72 px (5.6%) | 100% | 100% | 100% | 100% | 100% | 100% |
| 44 px (3.4%) | 100% | 100% | 100% | 100% | 100% | 100% |
| 24 px (1.9%) | 100% | 100% | 100% | 100% | 100% | 0% |
| 16 px (1.2%) | 67% | 100% | 100% | 25% | 8% | 0% |

Head-on, detection held down to 12 px, under 1% of frame width. Angle tolerance was complete to 70° provided the marker occupied about 44 px, or 3.4% of frame width.

Translated to a package, a 2 cm marker stays above 44 px out to roughly arm's length on a typical phone camera, at any angle a shopper would plausibly hold — the non-aim property, from a free library.

### 3.1 Re-measuring on a curved surface

Cosmetics packaging is mostly cylindrical. A marker wrapped around a bottle is not a plane seen at an angle: the further from the centre line, the more the surface turns away, so the marker's own squares compress unevenly across its width. A homography cannot express that.

We projected the marker onto a cylinder and measured again. The free parameter is the ratio of marker width to container circumference.

**Table 2.** Detection on a cylinder. Marker 120 px, twelve trials per condition.

| Marker width / circumference | 0° | 15° | 30° | 45° | 60° |
|---|---:|---:|---:|---:|---:|
| flat (label card) | 100% | 100% | 100% | 100% | 100% |
| 0.10 (wide jar, d = 70 mm) | 100% | 100% | 100% | 0% | 0% |
| 0.20 (serum bottle, d = 30 mm) | 100% | 100% | 0% | 0% | 0% |
| 0.30 | 100% | 100% | 0% | 0% | 0% |
| 0.40 (lip balm, d = 16 mm) | 100% | 0% | 0% | 0% | 0% |
| 0.50 | 100% | 0% | 0% | 0% | 0% |

Head-on detection is unaffected by curvature. What collapses is angle tolerance (Fig. 2).

This retracts much of the planar result. For a 20 mm marker: 30° on a wide jar, 15° on a serum bottle, head-on only on a lip balm.

### 3.2 The shape of the failure

On a flat surface, detection fails with size before it fails with angle (Fig. 1). On a curved one, angle binds first. The two constraints act together, so there are two design variables: the area a package can give up, and the curvature that area sits on.

## 4. Discussion

What ArUco does not carry is payload. A marker ID is a small integer rather than a URL, so a resolver mapping ID to product is required. NaviLens bundles that service; with ArUco it has to be built.

That is a reasonable trade at prototype stage, and it keeps the ingredient data under the researcher's control rather than a vendor's.

## 5. Scope boundary

The pipeline covers information access only. It does not assess ingredient safety, predict skin reactions, or rank products. The boundary is implemented in the output text rather than in a disclaimer: the summary closes by stating that it does not judge how ingredients act on skin.

This is a design constraint. A system built without dermatological training that sounds authoritative about cosmetic safety would be worse than no system, because it would be trusted.

## 6. Limitations

- The measurement uses synthetic scenes with no motion blur, no specular highlight off glossy surfaces, no rolling-shutter skew and no occlusion by fingers. It should be read as an upper bound.
- The cylinder measurement is also synthetic and excludes specular highlights. Glossy containers are the largest remaining untested factor.
- The ID-to-product resolver is not implemented.
- The allergen list is the EU's; Korean labelling rules were not cross-checked.
- No blind user has tried this. Detection rates and summary structure are measured and reasoned, not validated with readers.

### Expert-review candidates

- The marker area real cosmetics packaging can give up, and whether it clears 44 px at usable distances.
- Specular highlights on glossy containers, which the synthetic test cannot answer.
- Whether flagging an allergen is information access or interpretation. We drew that line on the access side and said so in the output, but without a dermatologist.

## 7. Conclusion

A non-aim recognition route exists without a commercial licence, but how forgiving it is depends on container shape: 70° on a flat label, 30° on a wide container, near head-on only on a narrow one. The constraints are package area and curvature. The ingredient summary conveys the label's content and what labelling rules single out, with interpretation placed explicitly out of scope.

## Reproduction

```
python scripts/marker_feasibility.py
python scripts/marker_cylinder.py
python -c "from pipeline.ingredient_summary import summarize; print(summarize('Water, Glycerin, Linalool'))"
```

## References

[1] Kim, Y. (2026). KOSHA-Braille: infrastructure-grade accessibility for Korean chemical safety information. *Universal Access in the Information Society*, 25, 116. https://doi.org/10.1007/s10209-026-01381-0

[2] Kim, Y. (in preparation). What Korean chemical names are made of. Paper 3 of this series.

[3] European Parliament and Council. Regulation (EC) No 1223/2009 on cosmetic products, Annex III.

[4] Garrido-Jurado, S., Muñoz-Salinas, R., Madrid-Cuevas, F. J., & Marín-Jiménez, M. J. (2014). Automatic generation and detection of highly reliable fiducial markers under occlusion. *Pattern Recognition*, 47(6), 2280-2292.

---

## Figures

**Fig. 1** ArUco detection rate on a flat surface, by marker size and off-axis angle. Failing cells cluster at the bottom (small markers) rather than at the right (wide angles). Twelve trials per condition, synthetic scenes. (`figures/Fig1.png`)

**Fig. 2** Detection on a cylinder. The larger the share of the container's circumference a marker spans, the narrower the angle tolerance. Head-on detection is unaffected by curvature. (`figures/Fig2.png`)

# Paper 4 — Outline (Draft v1)

## Working Title

**Reading a Cosmetics Label Without Aiming: Open Fiducial Markers and Structured
Ingredient Summaries as an Accessibility Route Where Braille Does Not Fit**

## Why braille runs out here

Papers 1-3 assume a page. A 30 ml bottle has none. Braille on cosmetics
packaging can carry a product name and little else, while the ingredient list —
the part a person with a fragrance allergy needs — is the longest text on the
label.

So this paper is the boundary case for the series: the domain where the
published approach does not extend, and the accessible route has to change
shape. Find the package, identify it without sight, hear the contents.

## Why QR is not the answer, and why that matters

A QR code must be framed: known location, roughly square on, close enough,
held still. Every one of those is a sighted precondition. Finding the code is
the task, and the code gives no help finding itself. That is why QR on
packaging has never worked for blind shoppers, and it is worth stating plainly
because QR keeps being proposed as an accessibility solution.

NaviLens exists because of that gap and has shipped — MTA New York, museums,
the Kellogg's Coco Pops trial. It is proprietary to Neosistec and licensed per
deployment.

## Contributions

1. **A measured open substitute.** ArUco markers ship with OpenCV and were
   designed for robot pose estimation, where the camera moves and the marker is
   wherever it is. Under synthetic degradation, detection is complete out to 70°
   off-axis when the marker occupies about 3.4% of frame width, and holds
   head-on down to 0.9%.

2. **The shape of the failure, which is the useful part.** Size binds before
   angle does. The design constraint is how much package area a marker can
   claim, not how carefully the user aims — the opposite of the QR assumption.

3. **An ingredient summariser** that restructures an INCI list along
   concentration order, EU Annex III labelling flags, and root decomposition
   reusing Paper 3's lexicon. Output is plain text sized for a TTS voice and
   passes unchanged through the published braille encoder.

4. **An explicit refusal to interpret.** The pipeline reports what the label
   says and what labelling rules single out. It does not assess safety. That
   boundary is enforced in the output text, not just in a disclaimer.

## Target venue

1. **ASSETS** — systems-and-users accessibility work, natural fit.
2. **UAIS** — continuity with Papers 1-2.
3. **CHI** (a11y subcommittee) — only with a user study, which this does not
   yet have.

## Status

| Component | State |
|---|---|
| NaviLens licensing survey | done, `docs/track-b-navilens-feasibility.md` |
| ArUco size/angle measurement | done, `scripts/marker_feasibility.py` |
| Ingredient summariser | implemented, `pipeline/ingredient_summary.py` |
| EU Annex III allergen list | 26 entries, EN + KO transliterations |
| ID-to-product resolver | not built |
| Curved-surface detection | not measured |
| Real INCI corpus | not obtained |
| User study | none |

## What has to happen before submission

- **Curved surfaces.** Cosmetics packaging is cylindrical; the measurement uses
  a planar homography. This is the largest gap between the number and reality.
- **A resolver service.** An ArUco ID is a small integer, not a URL. NaviLens
  bundles the mapping; here it must be built.
- **Real packaging footage.** The synthetic numbers are an upper bound with no
  motion blur, specular highlight or rolling shutter.

  The plan was 480 posed stills — three distances by five angles by two
  lightings by two exposures, across eight containers. That is the wrong medium
  and it was my error. Motion blur and rolling shutter exist only while the
  camera moves; posing for each of 480 frames removes two of the three artefacts
  the shoot exists to introduce, and costs an afternoon to do it.

  It is now four 20-second sweeps per container (lighting × exposure), six
  containers, **eight minutes of recording**. At 30 fps that is roughly 14,000
  frames against 480, the angle varies continuously rather than at five levels,
  and every frame carries the blur a hand actually produced.

  The angle for each frame comes from a large reference marker lying flat beside
  the container. Recovering it from the container's own marker would be
  circular — it works only where detection worked, so the failures, which are
  the data, would have no angle.

  Harness: `scripts/marker_video_eval.py`, exercised on a synthetic sweep.
  Sheet: `scripts/make_marker_sheet.py` now prints the reference marker and the
  sweep protocol. Neither crawling nor an API can substitute: the photographs
  have to contain *our marker*, and online product shots are the opposite
  condition — studio lit, square on, reflections removed.
- **At least one blind reader.** No user has tried this. A paper claiming an
  accessibility route without that is a systems paper, and should say so rather
  than imply otherwise.

## The line that needs an expert

Whether flagging an allergen is information access or interpretation. We drew
it on the access side and said so in the output, but that is a judgement made
without a dermatologist. It should not stay ours alone.

## Drafted material

- `docs/track-b-navilens-feasibility.md`
- `docs/track-b-followup-methods-draft.md`
- `docs/track-b-marker-measurements.json`

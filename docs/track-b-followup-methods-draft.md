# Track B — methods draft

Draft methods for a cosmetics-access paper. Two components: a non-aim scanning
route, and an ingredient-list summariser that produces speakable text.

## Why cosmetics resist braille

The published KOSHA-Braille work embosses MSDS text, which assumes a page. A
cosmetics package has no page. Braille on a 30 ml bottle can carry a product
name and little else, and the ingredient list — the part a person with an
allergy needs — is the longest text on the label.

So the accessible route cannot be embossing. It has to be: find the package,
identify it without sight, and hear the contents.

## Component 1: finding the package

Standard QR requires framing, which is the sighted precondition that makes QR
useless here. NaviLens solves it commercially; it is proprietary to Neosistec
and licensed per deployment.

ArUco fiducial markers, bundled with OpenCV, have the same non-aim property
because they were designed for robot pose estimation, where the camera is moving
and the marker is wherever it is.

We measured ArUco under synthetic degradation (perspective warp, blur, sensor
noise; twelve seeds per condition; 1280x720 frame). Detection is complete out to
70° off-axis provided the marker occupies about 44 px, and holds head-on down to
12 px — under 1% of frame width. Full table in
`docs/track-b-navilens-feasibility.md`.

The measurement is an upper bound: no motion blur, no specular highlight, no
rolling shutter, and a planar warp where cosmetics packaging is cylindrical. Its
value is the shape of the failure, which is that size binds before angle does.
The design constraint is therefore package area, not user aim.

What ArUco lacks is payload. A marker ID is a small integer, so a resolver has
to map ID to product. NaviLens bundles that service; here it must be built, in
exchange for the ingredient data staying under our control.

## Component 2: making the list speakable

An INCI list read verbatim is a minute of undifferentiated syllables. The
summariser restructures it along three axes.

**Concentration order.** INCI is ordered by descending concentration, so
position carries information that a flat reading discards. The summariser bands
the list and reads the head separately.

**Labelling flags.** EU Cosmetics Regulation 1223/2009 Annex III requires 26
fragrance allergens to be named on the label above a threshold. The summariser
reports which are present, in both English and Korean transliteration.

The wording matters. The output says these are ingredients the labelling rules
require to be named, and states explicitly that this does not mean they are
dangerous. An allergen list read in a warning tone would be a safety claim we
are not qualified to make.

**Root decomposition.** Ingredient names are decomposed with the chemical root
lexicon from Track A, so a name can be related to its parts. This is the reuse
that connects the two tracks: the Latin/Greek stock naming industrial chemicals
also names cosmetic ingredients. Where the label is English, the English side of
the same lexicon is used.

Output is plain text with no markup, sized for a TTS voice, and passes unchanged
through the published braille encoder for a refreshable display.

## Scope boundary

The pipeline reports what the label says and what the labelling rules single
out. It does not assess safety, predict skin reactions, rank products, or
recommend. That boundary is enforced in the output text itself, which closes by
saying the summary does not judge how ingredients act on skin.

This is a design constraint rather than a disclaimer. A system that sounds
authoritative about cosmetic safety, built by people without dermatological
training, would be worse than no system: it would be trusted.

## Limitations

- Marker measurements are synthetic and planar; cylindrical packaging is
  untested.
- The ID-to-product resolver is not built. The prototype covers marker detection
  and summarisation, not the service between them.
- The allergen list is the EU's. Korean labelling rules differ and have not been
  cross-checked.
- No blind user has tried any of this. Detection rates and summary structure are
  measured and reasoned, not validated with readers.

## Reproduction

```
python scripts/marker_feasibility.py     # rebuilds the detection tables
python -c "from pipeline.ingredient_summary import summarize; print(summarize('Water, Glycerin, Linalool'))"
```

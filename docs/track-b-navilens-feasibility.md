# Track B — non-aim scanning: what is available and what it costs

## The problem QR does not solve

A QR code has to be framed. The user points the camera at a known location,
roughly square on, close enough, and holds still. Every one of those is a
sighted precondition. That is why QR codes on packaging have never worked for
blind shoppers: finding the code is the task, and the code gives no help in
finding itself.

NaviLens exists because of that gap. Its claim is a *non-aim* read — the code is
picked up from several metres, well off-axis, while the camera sweeps. For
cosmetics, where the package is small and the ingredient list is long, that
property decides whether an accessibility route exists at all.

## NaviLens licensing

NaviLens is proprietary. Intellectual property and licensing sit with Neosistec,
the parent company. The reader app is free on iOS and Android, but publishing
codes requires a licence from Neosistec. Deployments are institutional —
transit authorities (MTA New York), museums, and the Kellogg's Coco Pops trial
in the UK — which is consistent with per-deployment licensing rather than a
public API tier.

No public pricing exists. Cost would have to be established by approaching
Neosistec directly, and that is a commercial decision outside this track.

## Open alternatives

Standard open-source scanners — ZXing, ZBar, html5-qrcode — read QR and
barcodes. They do not provide the non-aim property; they inherit QR's framing
requirement, so substituting them changes nothing for the user.

The open technology that does have the property is the fiducial marker: ArUco
(bundled with OpenCV) and AprilTag. These were built for robot pose estimation,
where the camera is moving and the marker is wherever it happens to be, so
detection at distance and angle is the design goal rather than an extra.

## Measurement

Rather than assert that ArUco is good enough, we measured it. A marker is
rendered, warped to simulate off-axis viewing, degraded with blur and sensor
noise, and placed in a 1280x720 frame. Twelve noise seeds per condition.

Detections out of 12:

| marker px | 0° | 15° | 30° | 45° | 60° | 70° |
|---:|---:|---:|---:|---:|---:|---:|
| 200 | 12 | 12 | 12 | 12 | 12 | 12 |
| 120 | 12 | 12 | 12 | 12 | 12 | 12 |
| 72 | 12 | 12 | 12 | 12 | 12 | 12 |
| 44 | 12 | 12 | 12 | 12 | 12 | 12 |
| 24 | 12 | 12 | 12 | 12 | 12 | 0 |
| 16 | 8 | 12 | 12 | 3 | 1 | 0 |

Head-on, detection holds down to 12 px — under 1% of frame width. Angle
tolerance is complete to 70° as long as the marker occupies about 44 px or more,
which on a 1280-wide frame is 3.4% of the width.

Translated to a package: a 2 cm marker stays above 44 px out to roughly an arm's
length on a typical phone camera, at any angle a shopper would plausibly hold.
That is the non-aim property, from a free library.

`scripts/marker_feasibility.py` reproduces the table;
`docs/track-b-marker-measurements.json` holds the raw counts.

### What the measurement does not cover

The scenes are synthetic. They have no motion blur, no specular highlight off a
glossy bottle, no rolling-shutter skew, no partial occlusion by fingers, and no
curved surface — cosmetics packaging is mostly cylindrical, which warps a marker
in a way a planar homography does not model. The numbers are an upper bound.

The informative part is the shape of the failure, not the ceiling: detection
degrades with size before it degrades with angle, so the design constraint is
how much package area a marker can claim, not how carefully the user aims.

## Where this leaves the track

A non-aim scanning route is available without a commercial licence. What ArUco
does not carry is payload: an ArUco ID is a small integer, not a URL, so a
resolver service has to map ID to product. NaviLens bundles that; with ArUco it
has to be built.

That is a reasonable trade for a prototype, and it keeps the ingredient data
under our control rather than a vendor's.

## Scope boundary

This track is information access only. Nothing here interprets ingredient
safety, predicts skin reactions, or ranks products. The pipeline reads what is
on the package and makes it available in a form a blind user can hear. Any
toxicological judgement is out of scope and must stay out, because a system that
sounds authoritative about safety while being built by non-experts is worse than
no system.

## Expert-review candidates

For a later consultation, scoped to single items rather than the whole design:

- Marker size against real cosmetics packaging: what area can a manufacturer
  actually give up, and does that clear 44 px at usable distances.
- Curved-surface detection rates, which the synthetic test cannot answer.
- Whether an allergen highlight is information access or interpretation. The
  line matters and we should not draw it alone.

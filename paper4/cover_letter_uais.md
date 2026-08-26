# Cover letter — *Universal Access in the Information Society*

**Manuscript:** Reading a Cosmetics Label Without Aiming: Open Fiducial Markers
and Structured Ingredient Summaries Where Braille Does Not Fit

**Author:** Yuyong Kim, University of Wisconsin-Madison
**ORCID:** 0009-0006-4842-666X
**Article type:** Brief Report

---

Dear Editors,

I am submitting this manuscript for consideration in *Universal Access in the
Information Society*. It follows *KOSHA-Braille: infrastructure-grade
accessibility for Korean chemical safety information* (25:116), and it is the
case where that paper's approach stops working.

**The boundary the paper is about.** The braille corpus in the earlier work
assumes a page. Cosmetics packaging has none. A 30 mL bottle can carry a product
name in braille and little else, while the ingredient list — the part a user
with a fragrance allergy actually needs — is the longest text on the label. When
the medium cannot be extended, the access route has to change shape rather than
be squeezed.

**What is reported.** Two components, each measured rather than asserted.

First, recognition that does not require aiming. QR is repeatedly proposed as an
accessibility answer and cannot be one: framing a code presupposes knowing where
it is, and finding it is the task. NaviLens exists because of that gap and is
licensed per deployment. We measured the open alternative, ArUco fiducial
markers, across marker size, off-axis angle, container curvature and specular
highlight.

Second, an ingredient summariser that restructures an INCI list by concentration
band, names the EU-labelled fragrance allergens, and decomposes ingredient names
into chemical roots, emitting plain text for a speech synthesiser or a
refreshable display.

**The result worth the editors' attention is a retraction.** On a flat surface
detection held to 70° off-axis. Wrapped onto a cylinder — which is what cosmetics
packaging is — angle tolerance collapsed: 30° on a wide jar, 15° on a serum
bottle, head-on only on a lip balm. The planar figure, which is what a
feasibility study would normally report, is optimistic to the point of being
misleading, and the paper says so and prints both.

**A bug the work found in itself.** The summariser's Korean allergen spellings
were my own transliterations. Checked one by one against the Korean Cosmetic
Association register, none was wrong, but only 12 of the 26 existed — so on a
Korean-market label the tool was passing silently over 14 declared allergens and
reporting nothing. It is now 25. A silent miss is the one failure this component
must not have, and it took a source of truth to find it.

**Stated plainly: no photographs were taken.** Every detection number is
synthetic. Curvature and specular highlight are modelled, not observed, and the
manuscript's limitations say what the model omits — coating texture, coloured
light, inter-reflection, and the interaction between gloss and off-axis angle,
which were never varied together. The synthetic sweep does make one testable
prediction, that detection turns over on the highlight's peak brightness rather
than the light's angular size, so exposure control matters more than the lamp.
That is the first thing photographs should check.

I submit it in that state deliberately. The curvature retraction and the
allergen gap are both findings that hold without photographs, and holding the
paper until a shoot is arranged would delay a correction to a claim — 70° on
flat packaging — that is already circulating in my own earlier work.

**Scope, kept out of the output as well as the text.** The pipeline reports what
the label states and what labelling rules single out. It does not assess
ingredient safety or predict skin reactions, and the summary's closing line says
so aloud rather than leaving it to a disclaimer the listener never hears. A
system built without dermatological training that sounded authoritative about
cosmetic safety would be worse than no system, because it would be believed.

**Companion submissions.** Two related manuscripts from the same series are
being submitted separately: one on the transliteration lexicon this paper's root
decomposition draws on, and one on evaluation protocol for Korean fingerspelling
recognition. They are independent papers, and I mention them so the editors can
see the relationship rather than discover it.

The manuscript is original, is not under consideration elsewhere, and has no
competing interests. It reports no work with human participants.

Thank you for your consideration.

Yuyong Kim
ykim288@wisc.edu

---

## Suggested reviewers

The paper is weakest where none of these has looked:

- Blind or low-vision shopping practice — whether a non-aim code is what the
  problem actually needs, or whether the difficulty is somewhere else entirely.
- Computer vision for fiducial markers — whether the cylinder and specular models
  are fair, and what a real photograph would be expected to show.
- Cosmetic regulatory labelling — whether flagging an allergen is information
  access or interpretation. I drew that line on the access side and said so in
  the output, but without a dermatologist.

## Note on prior art

NaviLens is the deployed system in this space. The paper cites it, describes its
licensing accurately as far as public information allows, and does not claim to
outperform it. The contribution is that an open route exists and how far it
actually reaches, which is narrower and checkable.

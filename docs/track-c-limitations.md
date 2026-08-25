# Track C — limitations

Written before results rather than after, so the list is not shaped by what
happened to work.

## Not evaluated on real data

No public Korean fingerspelling dataset was obtainable. Every number in
`track-c-fingerspelling-eval.md` comes from synthetic keypoints and measures the
harness, not recognition. Nothing here supports a claim about accuracy.

## Robustness untouched

The prototype does not address, and was not tested against:

- **Lighting.** MediaPipe degrades in low light and under strong directional
  light. Untested here.
- **Hand angle.** Landmarks are 3D, but a shape seen edge-on loses the
  information that separates similar jamo. The normalisation removes in-plane
  roll only; out-of-plane rotation is not handled.
- **Skin tone.** MediaPipe's hand detector has documented performance variation
  across skin tones. We have not measured it, and a system that works worse for
  darker-skinned signers is a fairness failure, not a technical footnote.
- **Hand size.** Palm-width scaling should cover adult variation. Children's
  hands and hands with different proportions are unverified.
- **Occlusion.** Fingers crossing or hiding each other, which several jamo
  require, gives MediaPipe unreliable landmarks. No handling.

## Scope boundaries

- **Static shapes only.** Any jamo that requires movement is outside this track.
  Whether Korean fingerspelling contains such jamo is an open question we have
  not answered, and it bounds how much of the alphabet this can ever cover.
- **No continuous signing.** Segmenting a fingerspelled word into letters is a
  different problem and is not attempted.
- **No sentence-level sign language.** Further still out of scope.

## Method limitations

- Nearest centroid assumes each jamo forms one cluster. A jamo signed two
  legitimate ways would be modelled as one blurred centroid and would score
  poorly for reasons that look like noise.
- Palm-width normalisation fails when the palm is edge-on and the two knuckles
  project onto nearly the same point. There is a fallback but it is weaker.
- No confidence output. The classifier always returns a label, including for a
  hand shape that is not a jamo at all.

## Who has not been consulted

No deaf signer, sign language linguist, or interpreter has reviewed any of this
— not the jamo inventory, not the assumption that static shapes suffice, not
whether a fingerspelling recognition tool is wanted.

That last question is the one to ask first. A hearing-led project can build a
technically sound recogniser for something the deaf community has no use for,
and the engineering being correct does not make the project worth doing.
Candidates for that consultation are listed at the end of
`track-c-fingerspelling-eval.md`.

# Cover letter — *Universal Access in the Information Society*

**Manuscript:** What Korean Chemical Names Are Made Of: A Mined Transliteration
Lexicon and the Registry Conventions It Cannot Cross

**Author:** Yuyong Kim, University of Wisconsin-Madison
**ORCID:** 0009-0006-4842-666X
**Article type:** Brief Report

---

Dear Editors,

I am submitting this manuscript for consideration in *Universal Access in the
Information Society*. It follows directly from work the journal published
earlier this year — *KOSHA-Braille: infrastructure-grade accessibility for
Korean chemical safety information* (25:116) — and reports a result that the
braille corpus described there made visible but could not explain.

**What the paper does.** The braille corpus rests on Korean chemical names,
which are transliterations of Latin- and Greek-derived English ones. If the
same roots recur across regulatory catalogues, one accessibility resource
extends to several; if not, every catalogue needs its own vocabulary work.
Rather than deriving a lexicon from naming rules, I mined one statistically
from 8,071 aligned Korean/English name pairs and then measured its reach across
three Korean regulatory registries: industrial chemicals (KOSHA), drug
ingredients (MFDS), and cosmetic ingredients (KCIA).

**What it found.** The answer splits in two, and the split is the contribution.
Chemical vocabulary does cross registry boundaries: the same roots appear in
all three catalogues. Orthographic convention does not, and the divergence is
systematic rather than incidental. On sodium and potassium the pharmaceutical
and cosmetic registers do not overlap by a single name — pharmacy writes 나트륨
and 칼륨, cosmetics writes 소듐 and 포타슘, and neither form appears in the
other register at all. Underneath the element names is a difference in
strategy: across 1,380 cosmetic ingredient names the register never once
translates a counter-ion into Sino-Korean, while pharmacy translates heavily
(염산 appears in 14.6% of drug ingredient names) and never transliterates.

**Why it belongs in this journal rather than a terminology venue.** The
divergence is not new to a Korean chemist, who resolves it from context without
noticing. It becomes a problem only when the reader has nothing but the string.
Print carries shape, colour and shelf position, all of which do identification
work that the words are not being asked to do. Braille and speech deliver the
word alone. A blind reader building a list of ingredients to avoid has no way
to know that the 소듐 on a shampoo bottle and the 나트륨 on a safety data sheet
are the same element, and no amount of care in the transliteration engine
recovers that, because the two forms are both correct and both official.

The cost of an inconsistency that print absorbs falls, in this case, almost
entirely on readers who cannot see the package. That asymmetry is the paper's
argument, and it is an accessibility argument.

**A methodological point the paper also records.** An earlier version of this
work reported 1.5% root coverage for pharmaceuticals and argued that the figure
described the measurement rather than the lexicon, because the reachable public
endpoint returns product names rather than ingredient names. That argument can
now be settled instead of asserted: measured on ingredient names from the same
agency, the same lexicon reaches 8.1%. Both rows are kept in Table 1. The gap
between them is the finding, and it is a failure mode easy to repeat, since a
public API that returns *something* for a drug query invites the assumption
that it returns ingredients.

**Reproducibility.** The lexicon, the mining method, the three conditions that
decide whether mining works, and every measurement script are released. Two
constraints are documented rather than worked around: the cosmetics dictionary's
terms of use prohibit redistribution, so the repository carries statistics
computed from a sample and never the entries themselves; and the drug register
is read through a service that already holds an authorised key, so no
credential is copied into the released code.

**Limitations, stated plainly.** Both ingredient catalogues were swept by search
rather than enumerated, so neither is a census. Drug ingredient names were
recovered from the parenthetical that Korean generics print after the product
name, which under-represents combination products. No transliteration reviewer
has audited the lexicon, and Section 6 lists the specific entries a reviewer
would be asked to confirm.

The manuscript is original, is not under consideration elsewhere, and has no
competing interests to declare. It reports no work with human participants.

Thank you for your consideration.

Yuyong Kim
ykim288@wisc.edu

---

## Suggested reviewers

Reviewers with one of the following would be most useful, and the paper is
weakest where none of them has looked:

- Korean transliteration or terminology standardisation — to check whether the
  registry conventions are described correctly and whether the divergence is
  known in the literature in a form I have missed.
- Chemical information systems — to check that the roots kept are chemically
  sensible and that the translated correspondences (*chloride* → 염화) are right
  for the registers claimed.
- Blind or low-vision reading practice — to check whether the access argument in
  Section 5.1 matches how a reader actually meets these names, rather than how I
  imagine they do.

## Alternate venue, if this is out of scope

If the editors judge the paper closer to terminology than to accessibility,
*Language Resources and Evaluation* would be the next fit: the released lexicon
and the measurement method would carry it there, though the argument in
Section 5.1 about who bears the cost would lose its audience.

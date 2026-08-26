# Cover letter — *Universal Access in the Information Society*

**Manuscript:** Person-Independent Evaluation for Korean Fingerspelling
Recognition, and Why the Split Is the Result

**Author:** Yuyong Kim, University of Wisconsin-Madison
**ORCID:** 0009-0006-4842-666X
**Article type:** Brief Report

---

Dear Editors,

I am submitting this manuscript for consideration in *Universal Access in the
Information Society*, and I want to be direct about what it is, because an
editor could reasonably desk-reject it on a misreading.

**This paper reports no recognition accuracy.** No Korean fingerspelling dataset
was obtainable, so every number in it comes from synthetic keypoints. The
manuscript says so in the abstract, in Section 4, and again in the limitations,
and the figures are captioned so a number cannot be lifted out of context. The
contribution is an evaluation protocol and the evidence for needing one.

**Why that is worth publishing rather than holding.** The series it belongs to
concerns accessibility infrastructure stopping at technical vocabulary. Chemical
names have no registered sign, so Korean Sign Language spells them with
지문자 — one static handshape per jamo. A recogniser for that would be useful.
Before building one, two things had to be checked, and both returned answers
that outlive any particular recogniser.

The first is measurable and was measured. On identical data, a random split
reported accuracy 4.2 points higher than a signer-grouped split. That gap is a
floor, since synthetic signer bias is more uniform than variation between real
hands.

The second is the finding I think justifies the paper. I audited the public
sign-alphabet datasets to see whether anyone *could* have run the
person-independent split. Of the seven whose schema resolves, none records who
signed the sample — including the 34,627-sample ASL-MNIST that most
fingerspelling papers report on, which stores only the image and its letter.
So the split is not merely neglected in this literature; on these datasets it is
not expressible, because the grouping variable was never captured. Every
accuracy published on them is a random split by construction and carries at
least the inflation measured here, whether or not its authors chose the protocol.

That reframes the field's numbers, it costs one integer column to fix, and the
column cannot be recovered after capture. It seemed worth saying now rather than
after I had collected my own data and quietly benefited from the same gap.

**What the paper does not do, and why that is deliberate.** It does not collect
Korean fingerspelling data. Before collecting, I want to ask Deaf signers whether
the tool is wanted, and that consultation has not happened yet. A hearing-led
project can build something technically sound that the Deaf community will not
use, and there is a documented concern that automatic recognition being "good
enough" creates pressure to reduce human interpreter provision. Section 5.4 says
who has not been consulted. The consultation protocol is written and released,
including — fixed before any answer is heard — what each possible answer does to
the study, since a question asked after the analysis is chosen can only ratify
it. If the answer is that the tool is not wanted, that is published as a finding.

**If the editors want data before publication**, I understand, and the honest
alternative is to hold the manuscript until the consultation concludes and, if it
is positive, a signer-grouped dataset exists. I would rather be told that than
have the synthetic figures mistaken for recognition results. But the dataset
audit does not depend on either outcome, and it is the part I would most like in
front of readers.

**Companion submissions.** Two related manuscripts from the same series are being
submitted separately, on a chemical transliteration lexicon and on cosmetics
label access. They are independent papers; I mention them so the relationship is
visible rather than discovered.

The manuscript is original, is not under consideration elsewhere, and has no
competing interests. It reports no work with human participants: the consultation
described in Section 5.4 has not been carried out, and no data from people were
collected or analysed.

Thank you for your consideration.

Yuyong Kim
ykim288@wisc.edu

---

## Suggested reviewers

The first of these matters more than the other two:

- A Deaf researcher or a Korean Sign Language linguist — to say whether the
  problem is framed in a way the community would recognise, and whether
  Section 5.4 is adequate or merely polite.
- Sign language recognition — to check the dataset audit against benchmarks I
  may have missed, and whether any carries signer identity in a form the schema
  does not expose.
- Machine learning evaluation methodology — to check the split comparison and
  whether the synthetic bias model understates or overstates the effect.

## A note on the negative result

I am aware that a paper reporting no accuracy figure is unusual, and that the
easy version of this work would have run the random split, published a high
number, and left the protocol argument out. That version would also have been
part of the problem the paper describes.

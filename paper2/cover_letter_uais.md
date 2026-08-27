# Cover letter — *Universal Access in the Information Society*

**Manuscript:** One Encoder, Three Registers: Extending Korean Braille
Infrastructure across Public-Safety Catalogues, and What Only a Narrative Domain
Reveals

**Author:** Yuyong Kim, University of Wisconsin-Madison
**ORCID:** 0009-0006-4842-666X
**Article type:** Original Article

---

Dear Editors,

I am submitting this manuscript for consideration in *Universal Access in the
Information Society*. It is the direct continuation of work the journal
published earlier this year — *KOSHA-Braille: infrastructure-grade accessibility
for Korean chemical safety information* (25:116) — and it settles a claim that
paper could only make prospectively.

**What the earlier paper left open.** Section VIII listed pharmaceutical labels
and first-aid protocols as candidate extensions. That was a statement about what
seemed possible, not a result. An encoder validated on one catalogue is not
thereby known to work on another, and the honest way to close the gap is to
apply it to catalogues that are actually shaped differently and report what
happens.

**What this paper does.** Three Korean national registers, one encoder, one
adapter each. Pharmaceutical approvals and patient leaflets, pesticide
registrations, and the KOSHA domestic accident-case board — 12,414 records,
encoded under the 2017 revised rules. Rule violations were zero in all three
domains and round-trip stability was 100%, 100%, and 99.8%. Median record length
spans more than two orders of magnitude while cells per source character stay
between 1.63 and 1.79: the shapes differ, the cost of embossing them barely
does.

**Why the third domain is the point.** Two of the three registers are records —
somebody filled in fields, and the adapter decides which field to read first. A
paper resting on those two alone would invite the obvious objection that the
shapes are not that different. The accident board is not a form: its content
field is a paragraph an investigator wrote, with a date, a time, and
measurements mid-sentence and no field boundary to lean on.

Adding it took stability from 100% to 99.5%, and that fall was two real defects.
A decoder that misread the roman terminator whenever a bracket or an unencodable
character appeared two words later, turning the Korean after it back into roman.
And an encoder that emitted the number indicator and then discarded subscript
digits, so H₂S came out as "H S" — silent loss in the one place a safety
catalogue cannot afford it, since the digit is what distinguishes hydrogen
sulfide from hydrogen. Both are fixed and both are reported with the material
that exposed them.

That is the paper's argument, and it is why I think it belongs here rather than
in a systems venue: **extensibility of accessibility infrastructure should be
judged not by whether a new domain can be attached but by what attaching it
reveals.** Had I stopped at the two record domains, the numbers would have read
100% and 100% and the encoder would have looked sturdier than it is.

**A methodological point about the metric.** Read by naive round-trip, the
pesticide domain scores 9.5% and looks broken. It is not. Rule 38 [proviso]
requires a space between a digit and an initial that shares its cell, so a
frequency of "3회" must be embossed as "3 회" and no decoder can put the space
back. Almost every pesticide row carries one. That score measures the writing
system, not the pipeline. The paper therefore reports round-trip three ways and
argues that the fixed-point test — encode and decode twice, and ask whether the
second pass changed anything — is the one that answers the correctness question.
I would rather make this explicit than publish a number that flatters the work.

**Reproducibility, including two things that cost me time.** All three fetchers,
the adapters, the validation harness and every figure script are released; the
collected source text is not redistributed, since all three registers are public
APIs a reader can call with their own key. Section 3.3 records two obstacles
that a later researcher will otherwise hit. First, the accident endpoint's
mandatory `callApiId` is documented as a "fixed value" whose value appears only
in an attached guide document, not on the dataset page. Second, and more
awkwardly, every direct call to the portal failed for an extended period with an
error naming the authentication key, which I diagnosed as an access problem and
worked around by routing through another service. The key was fine; the file it
was stored in used quoting my parser did not handle. I have written this up
because the error message points at the wrong thing, and because the workaround
I chose was avoidance rather than diagnosis.

**One result I did not expect.** Joining the three catalogues back to the
earlier work's chemical catalogue turned out to be governed not by chemistry but
by which language each agency writes in. The drug register names its active
ingredient in English, so the Korean chemical catalogue joins none of it — 0.0%
— while matching in English joins 46.3%. The pesticide register is the exact
mirror. And accident cases have no field naming a substance at all, so the loop
the earlier paper described — incident to data sheet to prevention — does not
close automatically. Section 7.4 reports this rather than the tidier claim I set
out to make.

**Limitations, stated plainly.** Only the accident board was collected in full;
pesticides are 3,000 of 95,912 rows, and the pharmaceutical register offers no
listing call, so its sample comes from sweeping dosage-form words and
under-represents products whose names lack them. Twenty accident cases (0.31%)
still do not reach a fixed point, at places where the cell stream genuinely does
not distinguish the readings. And nothing here is validated with braille
readers: the fixed reading orders are reasoned judgements, and the pesticide
adapter's decision to place toxicity last is the one I would most want a reader
to contradict.

The manuscript is original, is not under consideration elsewhere, and has no
competing interests to declare. It reports no work with human participants.

Thank you for your consideration.

Yuyong Kim
ykim288@wisc.edu

---

## Suggested reviewers

The paper is weakest where none of the following has looked:

- Braille production or transcription practice — to judge whether the reading
  orders in Section 5 serve a reader traversing linearly, and in particular
  whether placing toxicity last in the pesticide adapter is defensible or simply
  wrong.
- Korean braille standards — to check that the treatment of Rule 38 and the
  Rule 30 terminator is correct, since the validation metric rests on it.
- Open government data or civic technology — to judge whether the access
  findings in Section 3.3 generalise beyond the Korean portals, and whether the
  adapter structure is the right unit of reuse.

## Alternate venue, if this is out of scope

If the editors judge this closer to a systems contribution than to an
accessibility one, *ACM Transactions on Accessible Computing* would be the next
fit. The adapter structure and the per-domain validation would carry it there,
though the argument in Section 8.2 about secondary readers and parity of access
would have a narrower audience.

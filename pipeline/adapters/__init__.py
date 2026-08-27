"""Domain adapters: catalogue record in, braille-ready Korean text out.

Paper 1 encoded one catalogue, and the encoder turned out to be the reusable
part. What is not reusable is the shape of the source: an MSDS is sixteen
numbered sections, a drug label is a handful of prose fields, a pesticide
registration is a crop-by-pest table, and an incident report is a narrative.
Each needs its own reading, and none of them needs its own braille rules.

So the split is: an adapter knows one catalogue's field names and reading order
and produces plain Korean text; `pipeline.ko_braille` turns that into cells and
does not know which catalogue it came from. Adding a domain means writing one
adapter, not touching the encoder.

Reading order is the part that carries judgement rather than plumbing. A record
has no inherent order — the API returns whatever the database stores — and a
braille reader traverses linearly with no way to skim back. So each adapter
fixes an order and says why, and puts what a reader is most likely to be
looking for first rather than reproducing the field order of the source system.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# A comma and the initial ㄹ occupy the same cell (⠐). Print gets away with
# "현장에서,달비계에" because the eye sees the comma sitting low; braille cannot,
# and the decoder reads 현장에서달비계에 with a stray ㄹ. The two are genuinely
# indistinguishable in the cell stream, so the space has to be there before the
# text is encoded. Written Korean would have used one anyway — the omission is
# an artefact of typing into a database field, and it shows up in every domain,
# which is why the fix lives here rather than in one adapter.
#
# Hangul on both sides, and only there. The ambiguity exists because the cell
# after the comma could be read as an initial ㄹ, which requires a Korean
# syllable to follow; anything else is disambiguated by the number indicator or
# the roman indicator. Widening the rule breaks real notation — "3,200 mg"
# becomes two numbers one of which is a dose, "B1, B2" gains a second space,
# and "N,N-디메틸" is pulled apart. An earlier version did all three.
_COMMA_RUN = re.compile(r"(?<=[가-힣]),(?=[가-힣])")

# Subscript and superscript digits have no cell, and the encoder drops them
# after emitting the number indicator: "H₂S" comes out as "H S". That is silent
# loss in the one place these catalogues cannot afford it, since the digit is
# what distinguishes 황화수소 from 수소. Braille has no raised or lowered
# position either way, so the digit is written on the line — "H2S" — which is
# also how a chemist reads the formula aloud.
_SCRIPT_DIGITS = str.maketrans(
    "₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹",
    "01234567890123456789",
)


def normalise_for_braille(value) -> str:
    """Collapse the whitespace a source system leaves behind, and space commas.

    Braille has no run of blanks to spare: a document is measured in cells and
    a doubled space costs one. Source text is full of them — pasted line breaks,
    aligned columns, trailing tabs — and none of it means anything once the text
    is linear.
    """
    if value is None:
        return ""
    text = str(value).translate(_SCRIPT_DIGITS)
    return _COMMA_RUN.sub(", ", re.sub(r"\s+", " ", text).strip())


@dataclass
class Section:
    """One titled block of a record, in reading order."""

    title: str
    text: str

    def as_text(self) -> str:
        return f"{self.title}: {self.text}" if self.title else self.text


@dataclass
class AdaptedRecord:
    """A catalogue record, read into ordered Korean prose.

    `record_id` and `name` stay separate from the sections because they index
    the dataset, and a reader searching for a product should not have to parse
    the first section to find out what they are holding.
    """

    domain: str
    record_id: str
    name: str
    sections: list[Section] = field(default_factory=list)
    meta: dict = field(default_factory=dict)

    def text(self) -> str:
        """The whole record as one Korean string, sections in reading order."""
        parts = [s.as_text() for s in self.sections if s.text and s.text.strip()]
        return "\n".join(parts)

    @property
    def text_chars(self) -> int:
        return len(self.text())


class Adapter:
    """What every domain adapter provides.

    Deliberately small. An adapter that needs more than this is usually one
    that has started doing the encoder's job.
    """

    domain = "base"

    def adapt(self, raw: dict) -> AdaptedRecord:
        raise NotImplementedError

    def adapt_many(self, raws) -> list[AdaptedRecord]:
        out = []
        for raw in raws:
            rec = self.adapt(raw)
            if rec is not None and rec.text().strip():
                out.append(rec)
        return out


__all__ = ["Adapter", "AdaptedRecord", "Section", "normalise_for_braille"]

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

from dataclasses import dataclass, field


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


__all__ = ["Adapter", "AdaptedRecord", "Section"]

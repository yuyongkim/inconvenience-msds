"""Korean industrial accident cases, read into braille-ready prose.

KOSHA's board is the one source in this paper that is not a form. A drug label
and a pesticide registration were both assembled by somebody filling in fields,
and an adapter for either is mostly a decision about which field to read first.
An accident case has two fields that matter and one of them is a paragraph an
investigator wrote:

    2026. 2. 27.(금) 20:57 경북 울진군 조명시설 설치 현장에서 차량탑재형
    고소작업대에 탑승하여 조명기구 조정 작업 후 …

That is the hard case for the encoder, and it is the reason this domain is in
the paper at all. Records let an encoder off lightly: field values are short,
punctuation is scarce, and the boundaries do the work that grammar would.
Prose gives it a date, a time, a measurement, and six clauses in one sentence,
which is where the 2017 rules actually bite.

Reading order is short because the source is:

    업종      which board the case came from, and the closest thing to a category
    사고 개요  the board's title, which is written as a summary of what happened
    사고 경위  the investigator's paragraph

The title comes before the paragraph deliberately. It is one line — "외벽 도장
작업 중 추락" — and a braille reader traverses linearly with no way to skim
ahead, so a reader deciding whether this case is the one they want should not
have to sit through a paragraph to find out. The paragraph then repeats what
the title said and continues; that redundancy is a cost worth paying in print
and worth much more in braille.

The attachment count is dropped. It is a number about the web page, not about
the accident, and a reader holding an embossed page cannot open an attachment.
"""

from __future__ import annotations

import re

from . import Adapter, AdaptedRecord, Section, normalise_for_braille

# The board writes a date as "2026. 2. 27.(금)" and sometimes as
# "2025. 11. 20. (목)". Both are the same date and neither is wrong, but the
# bracket rules (제54~56항) treat an opening bracket that follows a space
# differently from one that does not, so the two spellings would be embossed
# differently. Normalising here means a reader is not made to notice which
# investigator typed which.
_WEEKDAY = re.compile(r"\.\s*\(([월화수목금토일])\)")

# Investigators mark editorial asides with ※ and *. Neither is in the Korean
# braille tables, so an unhandled one becomes an unknown cell in the middle of a
# sentence. ※ opens an aside, which in speech is a parenthetical, so it is read
# out as one; a bare asterisk carries no meaning left to preserve once the
# typography is gone.
_ASIDE = re.compile(r"\s*※\s*")
_STAR = re.compile(r"(?<![\d])\*+\s*")


def _clean(value) -> str:
    return normalise_for_braille(value)


def _prose(value) -> str:
    """The investigator's paragraph, with typography that braille cannot carry."""
    text = _clean(value)
    if not text:
        return ""
    text = _WEEKDAY.sub(r". \1요일", text)
    text = _ASIDE.sub(". 참고. ", text)
    text = _STAR.sub("", text)
    return text.strip()


class IncidentAdapter(Adapter):
    """One accident case, read as a heading and a narrative."""

    domain = "incident"

    def adapt(self, raw: dict) -> AdaptedRecord | None:
        summary = _clean(raw.get("keyword"))
        story = _prose(raw.get("contents"))
        if not (summary or story):
            return None

        sections: list[Section] = []

        business = _clean(raw.get("business"))
        if business:
            sections.append(Section("업종", business))
        if summary:
            sections.append(Section("사고 개요", summary))
        if story:
            sections.append(Section("사고 경위", story))

        board = _clean(raw.get("boardno"))
        return AdaptedRecord(
            domain=self.domain,
            record_id=board or summary,
            name=summary or board,
            sections=sections,
            meta={
                "business": business,
                "board_no": board,
                # The board number opens with the date it was posted, which is
                # the only date the record carries in a machine-readable place.
                "posted": board[:8] if len(board) >= 8 and board[:8].isdigit() else "",
            },
        )


__all__ = ["IncidentAdapter"]

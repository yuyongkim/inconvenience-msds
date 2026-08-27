"""Korean drug labels, read into braille-ready prose.

Two MFDS services describe the same product from different angles, and neither
alone makes a usable label.

`DrbEasyDrugInfoService` (e약은요) is written for patients: what the drug is
for, how to take it, what to watch for. It is the text worth reading aloud.
`DrugPrdtPrmsnInfoService07` is the approval register: the active ingredient,
the classification, whether it is prescription-only. It is short and it is what
tells you whether the leaflet in front of you belongs to the box in your hand.

This adapter takes either or both, keyed on the item sequence number.

Reading order is the decision here. The source returns fields in database
order, which puts the company name first; a braille reader traverses linearly
and cannot skim back, so a leaflet that opens with the manufacturer wastes the
position that matters most. The order below is what someone holding a box wants
to settle, roughly in the order they would ask it:

    what is this        product and ingredient
    is it for me        indication
    how do I take it    dosage
    what could go wrong warnings, then interactions, then side effects
    where do I keep it  storage

The warning block comes before side effects on purpose. A contraindication
changes whether the drug should be taken at all; a side effect changes what to
watch for afterwards. Reading them the other way round buries the first one
under the longer text of the second.
"""

from __future__ import annotations

import re

from . import Adapter, AdaptedRecord, Section, normalise_for_braille

# e약은요 field -> section title, in reading order.
EASY_FIELDS = [
    ("efcyQesitm", "효능효과"),
    ("useMethodQesitm", "용법용량"),
    ("atpnWarnQesitm", "경고"),
    ("atpnQesitm", "사용상 주의사항"),
    ("intrcQesitm", "상호작용"),
    ("seQesitm", "부작용"),
    ("depositMethodQesitm", "보관방법"),
]

# Approval-register fields worth reading. The rest of the record is
# administrative (business numbers, image URLs) and is kept out of the text.
APPROVAL_FIELDS = [
    ("ITEM_INGR_NAME", "주성분"),
    ("SPCLTY_PBLC", "구분"),
    ("PRDUCT_TYPE", "분류"),
    ("ENTP_NAME", "업체"),
]

# The classification arrives as "[02190]기타의 순환계용약". The bracketed code is
# an internal key: it reads aloud as seven digits that mean nothing to a
# listener, and it costs a number indicator plus five cells in braille.
CLASS_CODE = re.compile(r"^\[\d+\]")

# Marketing suffixes the register carries inside the product name. They are not
# wrong, but "수출명:..." is addressed to a customs officer, not a patient.
EXPORT_NAME = re.compile(r"\s*[（(]?\s*수출\s*명\s*[:：].*$")


EMPTY = {"자료없음", "None", "null"}


def _clean(value) -> str:
    if value is None:
        return ""
    # The services use both real newlines and a literal backslash-n; the shared
    # normaliser only knows about whitespace. Everything after that — collapsing
    # runs, spacing a list comma without touching a grouping comma, folding
    # subscript digits onto the line — is the same in every domain and belongs
    # there rather than here.
    text = normalise_for_braille(str(value).replace("\\n", " "))
    return "" if text in EMPTY else text


class DrugAdapter(Adapter):
    """MFDS drug labels. Accepts an e약은요 record, an approval record, or both."""

    domain = "drug"

    def adapt(self, raw: dict) -> AdaptedRecord | None:
        easy = raw.get("easy") or (raw if "efcyQesitm" in raw else {})
        appr = raw.get("approval") or (raw if "ITEM_NAME" in raw else {})
        if not easy and not appr:
            return None

        name = _clean(appr.get("ITEM_NAME")) or _clean(easy.get("itemName"))
        if not name:
            return None
        name = EXPORT_NAME.sub("", name).strip()

        item_seq = (_clean(appr.get("ITEM_SEQ")) or _clean(easy.get("itemSeq"))
                    or name)

        sections: list[Section] = []
        for key, title in APPROVAL_FIELDS:
            value = _clean(appr.get(key))
            if not value:
                continue
            if key == "PRDUCT_TYPE":
                value = CLASS_CODE.sub("", value).strip()
            if value:
                sections.append(Section(title, value))

        for key, title in EASY_FIELDS:
            value = _clean(easy.get(key))
            if value:
                sections.append(Section(title, value))

        return AdaptedRecord(
            domain=self.domain,
            record_id=item_seq,
            name=name,
            sections=sections,
            meta={
                "ingredient_en": _clean(appr.get("ITEM_INGR_NAME")),
                "name_en": _clean(appr.get("ITEM_ENG_NAME")),
                "permit_date": _clean(appr.get("ITEM_PERMIT_DATE")),
                "prescription": _clean(appr.get("SPCLTY_PBLC")),
                "has_easy": bool(easy),
                "has_approval": bool(appr),
            },
        )


__all__ = ["DrugAdapter"]

"""Korean pesticide registrations, read into braille-ready prose.

The MFDS register carries one row per approved *use*, not per product: the same
pesticide appears once for apples and aphids, again for pears and mites, each
with its own dilution and application window. That is the right shape for a
database and the wrong shape for a label, because a grower holding a bottle
wants the one row that matches the crop in front of them.

So this adapter reads a row as a single instruction rather than as a record. The
order below is what someone standing in an orchard needs settled, in the order
they would ask it:

    what is this       product, brand, formulation
    what is it for     purpose, crop, pest
    how do I use it    method, timing, dilution, quantity, frequency
    how dangerous      human and livestock toxicity, ecological toxicity

Toxicity comes last, and that is a deliberate choice against the usual safety
convention of leading with the warning. A registration row already implies the
substance is approved for this crop; what decides whether it is used safely is
the dilution and the frequency, and those are useless if the reader has stopped
listening. The grade is short, so it lands better as the closing statement than
as an opening one the reader must hold through four fields of numbers.

Company and address fields are dropped. They fill a third of the record and
answer a question nobody asks while spraying.
"""

from __future__ import annotations

import re

from . import Adapter, AdaptedRecord, Section, normalise_for_braille

# Field, title, and whether an empty value is worth saying aloud.
USE_FIELDS = [
    ("PRPOS_DVS_CD_NM", "용도"),
    ("CROPS_NM", "작물"),
    ("SICKNS_HLSCT_NM_WEEDS_NM", "병해충 또는 잡초"),
    ("AGCHM_USE_MTHD", "사용방법"),
    ("USE_PPRTM", "사용적기"),
]

TOXICITY_FIELDS = [
    ("PERSN_LVSTCK_TOXCTY", "사람 및 가축 독성"),
    ("ECLGY_TOXCTY", "생태 독성"),
]

# The register writes "자료없음" and a bare hyphen for absent values, and both
# read aloud as content when they are not.
EMPTY = {"", "-", "--", "자료없음", "해당없음", "None", "null"}


def _clean(value) -> str:
    text = normalise_for_braille(value)
    return "" if text in EMPTY else text


def _dilution(raw: str) -> str:
    """Dilution arrives as a bare number meaning "one part in N"."""
    text = _clean(raw)
    if not text:
        return ""
    return f"{text}배 희석" if re.fullmatch(r"[\d,]+", text) else text


class PesticideAdapter(Adapter):
    """One approved use of one pesticide, as a spoken instruction."""

    domain = "pesticide"

    def adapt(self, raw: dict) -> AdaptedRecord | None:
        name = _clean(raw.get("PRDLST_KOR_NM"))
        if not name:
            return None

        brand = _clean(raw.get("BRND_NM"))
        shape = _clean(raw.get("MDC_SHAP_NM"))
        head = ", ".join(x for x in (brand, shape) if x)

        sections: list[Section] = []
        if head:
            sections.append(Section("상표 및 제형", head))

        for key, title in USE_FIELDS:
            value = _clean(raw.get(key))
            if value:
                sections.append(Section(title, value))

        dilution = _dilution(raw.get("DILU_DRNG"))
        if dilution:
            sections.append(Section("희석배수", dilution))

        qty = _clean(raw.get("USE_QTY"))
        unit = _clean(raw.get("USE_UNIT"))
        if qty:
            sections.append(Section("사용량", f"{qty} {unit}".strip()))

        times = _clean(raw.get("USE_TMNO"))
        if times:
            sections.append(Section("사용횟수", times))

        tox = [f"{title} {v}" for key, title in TOXICITY_FIELDS
               if (v := _clean(raw.get(key)))]
        if tox:
            sections.append(Section("독성", ". ".join(tox)))

        # 등록여부 only matters when it is not a plain yes: a cancelled or
        # expired registration changes whether the row should be acted on at
        # all, so it goes last where a caveat belongs.
        status = _clean(raw.get("REG_YN_NM"))
        if status and status not in {"등록", "Y", "예"}:
            sections.append(Section("등록 상태", status))

        return AdaptedRecord(
            domain=self.domain,
            record_id=_clean(raw.get("AGCHM_PRDLST_NO")) or _clean(raw.get("PRDLST_REG_NO")) or name,
            name=name,
            sections=sections,
            meta={
                "name_en": _clean(raw.get("PRDLST_ENG_NM")),
                "brand": brand,
                "crop": _clean(raw.get("CROPS_NM")),
                "purpose": _clean(raw.get("PRPOS_DVS_CD_NM")),
                "reg_no": _clean(raw.get("PRDLST_REG_NO")),
                "registered": status,
            },
        )


__all__ = ["PesticideAdapter"]

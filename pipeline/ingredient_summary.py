"""Turn a cosmetic ingredient list into something worth hearing aloud.

An INCI list is a long comma-separated string of Latin-derived names, ordered by
concentration. Read straight out by a screen reader it is a minute of syllables
with no structure. This reshapes it: what the product mostly is, what an
allergen-labelling rule flags, and what each name's roots say it is made of.

The roots come from the chemical lexicon in `pipeline.morphology`, which is the
point of reusing it — the same Latin/Greek stock that names industrial chemicals
names cosmetic ingredients.

Deliberately not here: any judgement about whether an ingredient is safe, mild,
harsh, or suitable for a skin type. The EU allergen list is a labelling rule, not
a risk assessment, and is used here only to say "the label rules single this
out". Interpretation belongs to a dermatologist, not to this file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from pipeline.morphology import load_lexicon, segment

# The 26 fragrance allergens that EU Cosmetics Regulation 1223/2009 Annex III
# requires to be named on the label above a concentration threshold. Listing one
# is a labelling fact, not a warning.
EU_LABELLED_ALLERGENS = {
    "amyl cinnamal", "amylcinnamyl alcohol", "anisyl alcohol", "benzyl alcohol",
    "benzyl benzoate", "benzyl cinnamate", "benzyl salicylate", "cinnamal",
    "cinnamyl alcohol", "citral", "citronellol", "coumarin", "eugenol",
    "farnesol", "geraniol", "hexyl cinnamal", "hydroxycitronellal",
    "isoeugenol", "limonene", "linalool", "methyl 2-octynoate",
    "alpha-isomethyl ionone", "evernia prunastri", "evernia furfuracea",
    "butylphenyl methylpropional", "hydroxyisohexyl 3-cyclohexene carboxaldehyde",
}

# The same allergens under the Korean names, so a Korean-market label matches
# too. Every spelling here except the two noted below is the standardised name
# from the Korean Cosmetic Association dictionary, checked entry by entry by
# `scripts/allergen_ko_check.py`. They are not our transliterations: a spelling
# off by one syllable makes the summariser read a declared allergen out as an
# ordinary ingredient, which is the one failure this component must not have.
ALLERGEN_KO = {
    "리날룰": "linalool", "리모넨": "limonene", "제라니올": "geraniol",
    "시트로넬올": "citronellol", "시트랄": "citral", "쿠마린": "coumarin",
    "유제놀": "eugenol", "벤질알코올": "benzyl alcohol", "벤질벤조에이트": "benzyl benzoate",
    "벤질살리실레이트": "benzyl salicylate", "파네솔": "farnesol", "신남알": "cinnamal",
    "알파-아이소메틸아이오논": "alpha-isomethyl ionone",
    "아밀신남알": "amyl cinnamal", "아밀신나밀알코올": "amylcinnamyl alcohol",
    "벤질신나메이트": "benzyl cinnamate",
    "부틸페닐메틸프로피오날": "butylphenyl methylpropional",
    "신나밀알코올": "cinnamyl alcohol", "헥실신남알": "hexyl cinnamal",
    "하이드록시시트로넬알": "hydroxycitronellal", "아이소유제놀": "isoeugenol",
    "메틸2-옥티노에이트": "methyl 2-octynoate",
    # Listed under their botanical INCI, so the Korean name is the lichen's.
    "참나무이끼추출물": "evernia prunastri", "나무이끼추출물": "evernia furfuracea",
    # Not in the Korean dictionary at all. Our transliteration, unverified: a
    # Korean label using another spelling will be missed.
    "아니스알코올": "anisyl alcohol",
}

# The 26th, hydroxyisohexyl 3-cyclohexene carboxaldehyde, has no Korean entry.
# It has been banned in EU cosmetics since August 2021, so its absence from a
# Korean register is expected rather than a gap to fill.
ALLERGENS_WITHOUT_KOREAN_NAME = {"hydroxyisohexyl 3-cyclohexene carboxaldehyde"}

_SPLIT = re.compile(r"[,、/]|\s{2,}")


@dataclass
class Ingredient:
    raw: str
    name: str
    position: int
    total: int
    labelled_allergen: str | None = None
    roots: list[str] = field(default_factory=list)

    @property
    def share_band(self) -> str:
        """INCI orders by descending concentration, so position carries meaning."""
        if self.position == 0:
            return "most"
        if self.position < max(3, self.total // 10):
            return "high"
        if self.position < self.total // 2:
            return "middle"
        return "trace"


def parse_list(text: str) -> list[Ingredient]:
    parts = [p.strip(" .;") for p in _SPLIT.split(text or "")]
    parts = [p for p in parts if p]
    lex = load_lexicon()

    out: list[Ingredient] = []
    for i, part in enumerate(parts):
        name = re.sub(r"\s+", " ", part).strip()
        low = name.lower()
        allergen = None
        if low in EU_LABELLED_ALLERGENS:
            allergen = low
        else:
            key = re.sub(r"\s+", "", name)
            if key in ALLERGEN_KO:
                allergen = ALLERGEN_KO[key]

        roots = [root.en for surface, root in segment(name, lex) if root is not None]
        if not roots:
            # INCI is usually written in English, and the lexicon indexes Korean.
            # Fall back to the English side of the same roots.
            roots = sorted(
                {r.en for r in lex if len(r.en) >= 4 and r.en in low},
                key=len, reverse=True,
            )[:4]
        out.append(
            Ingredient(
                raw=part, name=name, position=i, total=len(parts),
                labelled_allergen=allergen, roots=roots,
            )
        )
    return out


def summarize(text: str, *, max_spoken: int = 8) -> str:
    """A short spoken-form summary. Plain text, no markup, for a TTS voice."""
    items = parse_list(text)
    if not items:
        return "성분 목록을 읽지 못했습니다."

    lines: list[str] = [f"성분 {len(items)}가지."]

    head = [i for i in items if i.share_band in ("most", "high")]
    if head:
        lines.append("함량이 많은 순서로 " + ", ".join(i.name for i in head[:4]) + ".")

    flagged = [i for i in items if i.labelled_allergen]
    if flagged:
        lines.append(
            "표시 대상 향료 성분이 "
            + ", ".join(i.name for i in flagged)
            + ". 유럽 화장품 규정이 이름을 적도록 정한 성분입니다. "
            "위험하다는 뜻이 아니라, 알레르기가 있는 사람이 확인할 수 있게 한 것입니다."
        )
    else:
        lines.append("표시 대상 향료 성분은 없습니다.")

    spoken = {id(i) for i in head} | {id(i) for i in flagged}
    rest = [i for i in items if id(i) not in spoken][:max_spoken]
    if rest:
        lines.append("그 밖에 " + ", ".join(i.name for i in rest) + ".")
    remaining = len(items) - len(spoken) - len(rest)
    if remaining > 0:
        lines.append(f"나머지 {remaining}가지는 생략했습니다.")

    lines.append("성분이 피부에 어떻게 작용하는지는 이 요약이 판단하지 않습니다.")
    return " ".join(lines)

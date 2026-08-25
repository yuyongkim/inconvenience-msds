"""Chemical-name morphology: split a transliterated Korean name into roots.

Korean chemical names are transliterations of Latin/Greek-derived English ones.
"Chlorobenzene" becomes "클로로벤젠", and the same pieces recur across tens of
thousands of names: chloro/클로로, nitro/니트로, benzene/벤젠, -yl/-일.

The braille encoder does not need any of this — it maps syllables to cells and
never looks inside a word. The lexicon exists for the questions the encoder
cannot answer: which roots does a domain actually use, do two domains share
them, and is a given name transliterated the way its parts say it should be.

The lexicon is mined from the 111,556 aligned Korean/English name pairs in the
KOSHA database rather than hand-written, so it reflects the transliterations
that Korean regulatory text actually uses. See `scripts/mine_morphemes.py`.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEXICON_PATH = PROJECT_ROOT / "data" / "morphology" / "roots.json"

# Names carry their English gloss and trivial-name notes in parentheses.
_PAREN = re.compile(r"\s*\([^()]*\)")
_BRACKET = re.compile(r"\s*\[[^\[\]]*\]")
# Locants and stereo descriptors: "1,2-", "(E)-", "N,N'-", "sec-", "tert-".
_LOCANT = re.compile(r"(?:^|(?<=[\s,]))[0-9NOSRZEαβγ,'′\-]+-")


@dataclass(frozen=True)
class Root:
    """One morpheme and the Korean form(s) it is transliterated as."""

    en: str
    ko: tuple[str, ...]
    kind: str          # prefix | infix | suffix | stem
    count: int         # how many corpus names it was observed in

    @property
    def primary(self) -> str:
        return self.ko[0]


def strip_annotations(name: str) -> str:
    """Reduce a database name to the bare Korean term.

    '아조벤젠 (AZOBENZENE) (아조벤젠 ( 관용명 : ...' -> '아조벤젠'
    """
    if not name:
        return ""
    # Parentheses nest and are sometimes unbalanced, so strip repeatedly.
    prev = None
    out = name
    while out != prev:
        prev = out
        out = _PAREN.sub("", out)
        out = _BRACKET.sub("", out)
    # An unbalanced '(' leaves a tail behind.
    out = out.split("(")[0]
    return out.strip()


def normalize_en(name: str) -> str:
    out = strip_annotations(name).lower()
    out = _LOCANT.sub("", out)
    return re.sub(r"[^a-z]+", "", out)


def normalize_ko(name: str) -> str:
    out = strip_annotations(name)
    out = _LOCANT.sub("", out)
    return re.sub(r"[^가-힣]+", "", out)


@lru_cache(maxsize=1)
def load_lexicon(path: str | None = None) -> tuple[Root, ...]:
    src = Path(path) if path else LEXICON_PATH
    if not src.exists():
        return ()
    raw = json.loads(src.read_text(encoding="utf-8"))
    roots = [
        Root(en=r["en"], ko=tuple(r["ko"]), kind=r["kind"], count=r["count"])
        for r in raw["roots"]
    ]
    # Longest first so "클로로" wins over "클로" when both could match.
    roots.sort(key=lambda r: (-len(r.primary), -r.count))
    return tuple(roots)


def segment(korean_name: str, lexicon: tuple[Root, ...] | None = None) -> list[tuple[str, Root | None]]:
    """Greedily split a Korean chemical name into (surface, root) pieces.

    Unmatched stretches come back with a None root, which is what the coverage
    report counts.
    """
    text = normalize_ko(korean_name)
    roots = lexicon if lexicon is not None else load_lexicon()
    if not text:
        return []
    if not roots:
        return [(text, None)]

    pieces: list[tuple[str, Root | None]] = []
    unmatched: list[str] = []
    i = 0
    while i < len(text):
        hit = None
        for root in roots:
            for form in root.ko:
                if form and text.startswith(form, i):
                    hit = (form, root)
                    break
            if hit:
                break
        if hit is None:
            unmatched.append(text[i])
            i += 1
            continue
        if unmatched:
            pieces.append(("".join(unmatched), None))
            unmatched = []
        pieces.append(hit)
        i += len(hit[0])
    if unmatched:
        pieces.append(("".join(unmatched), None))
    return pieces


def coverage(korean_name: str, lexicon: tuple[Root, ...] | None = None) -> float:
    """Fraction of the name's Hangul that a known root accounts for."""
    pieces = segment(korean_name, lexicon)
    total = sum(len(surface) for surface, _ in pieces)
    if not total:
        return 0.0
    matched = sum(len(surface) for surface, root in pieces if root is not None)
    return matched / total

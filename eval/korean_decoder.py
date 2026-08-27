"""
Strict Korean braille decoder helpers for evaluation scripts.

Evaluation must fail closed when the Korean decoder is unavailable.
Silently returning braille cells as text produces misleading metrics.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Callable


DECODER_QUALNAME = "pipeline.ko_braille_decoder.decode_korean_braille"


@lru_cache(maxsize=1)
def _load_decoder() -> Callable[[str], str]:
    """Load the repository's Korean braille decoder or raise loudly."""
    try:
        from pipeline.ko_braille_decoder import decode_korean_braille
    except Exception as exc:  # pragma: no cover - import failure path
        raise RuntimeError(
            f"Unable to import Korean braille decoder ({DECODER_QUALNAME}). "
            "KR evaluation cannot proceed without the real decoder."
        ) from exc

    return decode_korean_braille


def decode_ko_braille_strict(braille_text: str) -> str:
    """Decode Korean braille using the project decoder and validate the result."""
    if not braille_text:
        return ""

    decoded = _load_decoder()(braille_text)
    if not isinstance(decoded, str):
        raise TypeError(
            f"{DECODER_QUALNAME} returned {type(decoded).__name__}, expected str."
        )
    return decoded

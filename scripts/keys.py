"""Read API keys out of .env without mangling them.

A naive `split("=", 1)` loop is what most of these scripts started with, and it
is wrong in two ways that both cost real time here.

First, a quoted value keeps its quotes. `data="ABC"` yields `"ABC"`, and
`requests` dutifully percent-encodes the quotes into the query string, so the
portal sees `%22ABC%22` and answers SERVICE_KEY_IS_NOT_REGISTERED_ERROR. The
error names the key, so it reads as an authorisation problem, and it is not.

Second, a quoted value may span lines. The data.go.kr key in this project's
.env was pasted with a line break before its closing quote, which a line-at-a-
time reader truncates silently — again producing a plausible-looking key that
the portal rejects.

So this parses the file as a whole, honours quotes, and folds whitespace out of
the value. Keys never legitimately contain whitespace; a break inside one is
always an artefact of pasting.

data.go.kr issues each key twice, encoded and decoded, and the two are the same
key. `requests` encodes query parameters itself, so it must be handed the
decoded form or the percent signs get escaped a second time. `service_key`
returns the decoded form whichever way the file stores it.
"""

from __future__ import annotations

import re
import urllib.parse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Fallback for keys this project shares with the chemical information service.
MSDS_ENV = Path("G:/MSDS/.env")

_ENTRY = re.compile(
    r"""^[ \t]*(?P<name>[A-Za-z_][A-Za-z0-9_]*)[ \t]*=[ \t]*
        (?: "(?P<dq>[^"]*)" | '(?P<sq>[^']*)' | (?P<bare>[^\r\n]*) )""",
    re.M | re.X | re.S,
)


def load_env(path: Path) -> dict[str, str]:
    """Every assignment in one .env, with quotes honoured and values de-spaced."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    out: dict[str, str] = {}
    for m in _ENTRY.finditer(text):
        value = m.group("dq") or m.group("sq") or m.group("bare") or ""
        out[m.group("name").lower()] = re.sub(r"\s+", "", value)
    return out


def _all() -> dict[str, str]:
    env = load_env(MSDS_ENV)
    env.update(load_env(PROJECT_ROOT / ".env"))  # this project wins on a clash
    return env


def get(*names: str) -> str:
    """First of `names` that is present, searched in this project then MSDS."""
    env = _all()
    for name in names:
        value = env.get(name.lower())
        if value:
            return value
    raise SystemExit(f"none of {names} found in .env")


def service_key(*names: str) -> str:
    """A data.go.kr key in the decoded form `requests` needs.

    Unquoting a decoded key is a no-op, so this is safe either way: the decoded
    form contains `+` and `=` but no percent escapes.
    """
    return urllib.parse.unquote(get(*(names or ("data", "kosha_service_key_decoded"))))


__all__ = ["load_env", "get", "service_key", "PROJECT_ROOT"]

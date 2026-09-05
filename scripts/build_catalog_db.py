"""Turn the exported catalogues into a database the web service can search.

The MSDS side of the site reads SQLite, and the paper-2 catalogues are JSONL —
good for distribution, useless for a search box. 145,262 records is far past
what a live service should hold in memory, and the site runs on a machine that
is doing other things.

So this builds one SQLite file with an FTS5 index. Braille is not stored: the
encoder takes about a millisecond per record and storing it would double the
file for a value that is derived. The MSDS path already encodes on request.

Sections are kept as JSON on the row rather than in a table of their own. They
are only ever read whole, in order, for one record at a time; a join would buy
nothing and would lose the ordering that is the adapters' entire contribution.

Usage:
    python scripts/build_catalog_db.py
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATASET = PROJECT_ROOT / "data" / "paper2_dataset"
OUT = PROJECT_ROOT / "data" / "catalog.db"

# Config -> what the tab is called and what one record is. The label is here
# rather than in the frontend because the API should be able to describe itself;
# a client that has to hardcode the Korean for each config is a client that goes
# stale when a config is added.
CATALOGS = {
    "drug_leaflet": {
        "label": "의약품 복약정보",
        "unit": "품목",
        "source": "식품의약품안전처 · e약은요 + 허가정보",
    },
    "drug_approval": {
        "label": "의약품 허가정보",
        "unit": "품목",
        "source": "식품의약품안전처 · 허가정보",
    },
    "pesticide": {
        "label": "농약 등록정보",
        "unit": "승인된 사용",
        "source": "식품의약품안전처 · 식품안전나라",
    },
    "incident": {
        "label": "산업재해 사례",
        "unit": "사례",
        "source": "한국산업안전보건공단 · 국내재해사례",
    },
}

SCHEMA = """
CREATE TABLE catalog (
    config     TEXT NOT NULL,
    record_id  TEXT NOT NULL,
    name       TEXT NOT NULL,
    text       TEXT NOT NULL,
    sections   TEXT NOT NULL,
    meta       TEXT NOT NULL,
    text_chars INTEGER NOT NULL,
    PRIMARY KEY (config, record_id)
);

CREATE TABLE catalog_info (
    config  TEXT PRIMARY KEY,
    label   TEXT NOT NULL,
    unit    TEXT NOT NULL,
    source  TEXT NOT NULL,
    records INTEGER NOT NULL
);

-- The search box is the reason this file exists, so the index covers the name
-- and the body. Searching the body matters more here than for a chemical
-- catalogue: somebody looking for an accident involving a ladder has no name
-- to type.
--
-- The tokenizer has to be trigram. Korean does not space its compounds, so the
-- default word tokenizer indexes 타이레놀정500밀리그람 as one token and a search
-- for 타이레놀 finds nothing — which is exactly what a user would type. Trigram
-- costs roughly twice the index size and buys substring search, which for this
-- language is not a refinement but the difference between working and not.
CREATE VIRTUAL TABLE catalog_fts USING fts5(
    name, text, config UNINDEXED, record_id UNINDEXED,
    tokenize = 'trigram'
);
"""


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(OUT))
    args = ap.parse_args()

    out = Path(args.output)
    tmp = out.with_suffix(".db.tmp")
    tmp.unlink(missing_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(tmp)
    con.executescript(SCHEMA)

    total = 0
    for config, info in CATALOGS.items():
        path = DATASET / f"{config}.jsonl"
        if not path.exists():
            print(f"{config}: no export, skipped")
            continue
        rows = []
        for rec in load(path):
            rows.append((
                config, rec["record_id"], rec["name"], rec["text"],
                json.dumps(rec.get("sections", []), ensure_ascii=False),
                json.dumps(rec.get("meta", {}), ensure_ascii=False),
                rec.get("text_chars") or len(rec["text"]),
            ))
        con.executemany(
            "INSERT OR REPLACE INTO catalog "
            "(config, record_id, name, text, sections, meta, text_chars) "
            "VALUES (?,?,?,?,?,?,?)", rows)
        con.executemany(
            "INSERT INTO catalog_fts (name, text, config, record_id) "
            "VALUES (?,?,?,?)",
            [(r[2], r[3], r[0], r[1]) for r in rows])
        con.execute(
            "INSERT OR REPLACE INTO catalog_info "
            "(config, label, unit, source, records) VALUES (?,?,?,?,?)",
            (config, info["label"], info["unit"], info["source"], len(rows)))
        total += len(rows)
        print(f"{config:16s} {len(rows):>7,} records", flush=True)

    con.commit()
    con.execute("ANALYZE")
    con.commit()
    con.close()

    # Swap at the end so a half-built file is never what the service opens.
    out.unlink(missing_ok=True)
    tmp.rename(out)

    print(f"\n{total:,} records  ->  {out}  "
          f"({out.stat().st_size / 1024 / 1024:.0f} MB)")


if __name__ == "__main__":
    main()

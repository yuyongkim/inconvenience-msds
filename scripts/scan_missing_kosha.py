"""
Scan KOSHA chem_id range to discover and fetch missing chemicals.

Probes IDs not in the DB. When data exists, fetches all 16 sections.
Rate: 0.5s per call. Estimated time for 0-50000 range: ~3-4 hours.

Usage:
    python scripts/scan_missing_kosha.py --start 0 --end 50000
    python scripts/scan_missing_kosha.py --start 0 --end 50000 --workers 2
    python scripts/scan_missing_kosha.py --start 0 --end 1000 --test  # quick test

Resume-safe: skips IDs already in DB.
Ctrl+C to stop gracefully.
"""

import os
import argparse
import logging
import signal
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = "G:/MSDS/data/terminology.db"
BASE_URL = "https://apis.data.go.kr/B552468/msdschem"
API_KEY = os.environ.get("DATA_GO_KR_SERVICE_KEY", "")
if not API_KEY:
    raise SystemExit(
        "DATA_GO_KR_SERVICE_KEY is not set. Request a service key at "
        "data.go.kr and set it in the environment before running this script."
    )
RATE_LIMIT = 0.5
_shutdown = False


def _signal_handler(sig, frame):
    global _shutdown
    logger.info("Stopping after current batch...")
    _shutdown = True

signal.signal(signal.SIGINT, _signal_handler)


def get_existing_ids(db_path: str) -> set[str]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT chem_id FROM msds_details")
    ids = {r[0] for r in cur.fetchall()}
    conn.close()
    return ids


def probe_id(chem_id: str) -> bool:
    """Quick check if a chem_id has data (section 1 only)."""
    try:
        r = requests.get(f"{BASE_URL}/getChemDetail01", params={
            "serviceKey": API_KEY,
            "chemId": chem_id,
        }, timeout=10)
        return r.status_code == 200 and "<itemDetail>" in r.text
    except Exception:
        return False


def fetch_all_sections(chem_id: str) -> dict[int, str]:
    """Fetch all 16 sections for a chemical."""
    sections = {}
    for sec in range(1, 17):
        if _shutdown:
            break
        try:
            r = requests.get(f"{BASE_URL}/getChemDetail{sec:02d}", params={
                "serviceKey": API_KEY,
                "chemId": chem_id,
            }, timeout=10)
            if r.status_code == 200 and "<itemDetail>" in r.text:
                sections[sec] = r.text
        except Exception:
            pass
        time.sleep(RATE_LIMIT)
    return sections


def save_sections(db_path: str, chem_id: str, sections: dict[int, str]):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA busy_timeout=30000")
    for sec_no, xml_data in sections.items():
        conn.execute(
            "INSERT OR REPLACE INTO msds_details (chem_id, section_no, xml_data) VALUES (?, ?, ?)",
            (chem_id, sec_no, xml_data)
        )
    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=50000)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--db", default=DB_PATH)
    parser.add_argument("--test", action="store_true", help="Quick test mode")
    args = parser.parse_args()

    if args.test:
        args.end = min(args.end, args.start + 100)

    existing = get_existing_ids(args.db)
    logger.info(f"Existing: {len(existing)} chemicals")

    # Generate candidate IDs
    candidates = []
    for i in range(args.start, args.end + 1):
        cid = f"{i:06d}"
        if cid not in existing:
            candidates.append(cid)

    logger.info(f"Candidates to scan: {len(candidates)} (range {args.start}-{args.end})")

    discovered = 0
    probed = 0
    start_time = time.time()

    for cid in candidates:
        if _shutdown:
            break

        # Probe
        has_data = probe_id(cid)
        probed += 1
        time.sleep(RATE_LIMIT)

        if has_data:
            logger.info(f"FOUND: {cid} — fetching 16 sections...")
            sections = fetch_all_sections(cid)
            if sections:
                save_sections(args.db, cid, sections)
                discovered += 1
                logger.info(f"  Saved {len(sections)} sections for {cid}")

        if probed % 100 == 0:
            elapsed = time.time() - start_time
            rate = probed / elapsed if elapsed > 0 else 0
            eta = (len(candidates) - probed) / rate / 3600 if rate > 0 else 0
            logger.info(f"Probed: {probed}/{len(candidates)}, "
                        f"discovered: {discovered}, "
                        f"rate: {rate:.1f}/s, ETA: {eta:.1f}h")

    elapsed = time.time() - start_time
    logger.info(f"\nDone: probed {probed}, discovered {discovered} in {elapsed/60:.0f}min")


if __name__ == "__main__":
    main()

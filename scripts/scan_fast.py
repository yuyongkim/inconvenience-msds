"""
Fast 2-phase KOSHA scanner.

Phase 1: Probe all IDs in parallel (section 1 only) — find which exist
Phase 2: Fetch all 16 sections for discovered IDs in parallel

This is much faster than probe+fetch in one pass.

Usage:
    python scripts/scan_fast.py --start 3740 --end 50000 --workers 16
"""

import os
import argparse
import json
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
_shutdown = False
def _signal_handler(sig, frame):
    global _shutdown
    logger.info("Stopping...")
    _shutdown = True
signal.signal(signal.SIGINT, _signal_handler)


def get_existing_ids(db_path: str) -> set[str]:
    conn = sqlite3.connect(db_path)
    ids = {r[0] for r in conn.execute("SELECT DISTINCT chem_id FROM msds_details").fetchall()}
    conn.close()
    return ids


def probe_one(chem_id: str) -> tuple[str, bool, str | None]:
    """Probe section 1 only. Returns (chem_id, exists, xml_or_none)."""
    try:
        r = requests.get(f"{BASE_URL}/getChemDetail01", params={
            "serviceKey": API_KEY, "chemId": chem_id
        }, timeout=8)
        if r.status_code == 200 and "<itemDetail>" in r.text:
            return (chem_id, True, r.text)
        if r.status_code == 429:
            time.sleep(10)
        return (chem_id, False, None)
    except Exception:
        return (chem_id, False, None)


def fetch_section(chem_id: str, sec: int) -> tuple[str, int, str | None]:
    """Fetch one section."""
    try:
        r = requests.get(f"{BASE_URL}/getChemDetail{sec:02d}", params={
            "serviceKey": API_KEY, "chemId": chem_id
        }, timeout=8)
        if r.status_code == 200 and "<resultCode>00</resultCode>" in r.text:
            return (chem_id, sec, r.text if "<itemDetail>" in r.text else None)
        if r.status_code == 429:
            time.sleep(10)
        return (chem_id, sec, None)
    except Exception:
        return (chem_id, sec, None)


def save_sections(db_path: str, items: list[tuple[str, int, str]]):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executemany(
        "INSERT OR REPLACE INTO msds_details (chem_id, section_no, xml_data) VALUES (?, ?, ?)",
        [(cid, sec, xml) for cid, sec, xml in items if xml]
    )
    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=3740)
    parser.add_argument("--end", type=int, default=50000)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--db", default=DB_PATH)
    args = parser.parse_args()

    existing = get_existing_ids(args.db)
    candidates = [f"{i:06d}" for i in range(args.start, args.end + 1) if f"{i:06d}" not in existing]
    logger.info(f"Phase 1: Probing {len(candidates)} IDs with {args.workers} workers...")

    # ---- Phase 1: Probe ----
    discovered = []  # (chem_id, sec1_xml)
    probed = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(probe_one, cid): cid for cid in candidates}

        for future in as_completed(futures):
            if _shutdown:
                break
            cid, exists, xml = future.result()
            probed += 1
            if exists:
                discovered.append((cid, xml))

            if probed % 500 == 0:
                elapsed = time.time() - start
                rate = probed / elapsed
                eta = (len(candidates) - probed) / rate / 60
                logger.info(f"  Probed {probed}/{len(candidates)}, found {len(discovered)}, "
                           f"{rate:.0f}/s, ETA {eta:.0f}min")

    elapsed = time.time() - start
    logger.info(f"Phase 1 done: {probed} probed, {len(discovered)} found in {elapsed/60:.1f}min")

    # Save section 1 data immediately
    sec1_items = [(cid, 1, xml) for cid, xml in discovered if xml]
    if sec1_items:
        save_sections(args.db, sec1_items)
        logger.info(f"Saved {len(sec1_items)} section-1 records")

    if _shutdown or not discovered:
        return

    # ---- Phase 2: Fetch remaining sections (2-16) ----
    logger.info(f"Phase 2: Fetching sections 2-16 for {len(discovered)} chemicals...")

    fetch_tasks = []
    for cid, _ in discovered:
        for sec in range(2, 17):
            fetch_tasks.append((cid, sec))

    saved_count = 0
    batch = []
    start = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(fetch_section, cid, sec): (cid, sec) for cid, sec in fetch_tasks}

        for future in as_completed(futures):
            if _shutdown:
                break
            cid, sec, xml = future.result()
            if xml:
                batch.append((cid, sec, xml))

            # Save in batches of 100
            if len(batch) >= 100:
                save_sections(args.db, batch)
                saved_count += len(batch)
                batch = []

            if saved_count % 500 == 0 and saved_count > 0:
                elapsed = time.time() - start
                total_tasks = len(fetch_tasks)
                done = saved_count + len(batch)
                logger.info(f"  Phase 2: {done}/{total_tasks} sections saved")

    # Save remaining
    if batch:
        save_sections(args.db, batch)
        saved_count += len(batch)

    elapsed = time.time() - start
    logger.info(f"Phase 2 done: {saved_count} sections in {elapsed/60:.1f}min")

    # Final count
    conn = sqlite3.connect(args.db)
    total = conn.execute("SELECT COUNT(DISTINCT chem_id) FROM msds_details").fetchone()[0]
    conn.close()
    logger.info(f"DB total: {total} chemicals")


if __name__ == "__main__":
    main()

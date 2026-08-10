"""
Parallel KOSHA MSDS scanner.

Splits ID range into chunks and runs them concurrently with ThreadPoolExecutor.
Rate limit: controlled per-worker to stay within API limits.

Usage:
    python scripts/scan_parallel.py                      # default: 8 workers
    python scripts/scan_parallel.py --workers 10
    python scripts/scan_parallel.py --start 3740 --end 50000 --workers 10
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(threadName)s] %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = "G:/MSDS/data/terminology.db"
BASE_URL = "https://apis.data.go.kr/B552468/msdschem"
API_KEY = os.environ.get("DATA_GO_KR_SERVICE_KEY", "")
if not API_KEY:
    raise SystemExit(
        "DATA_GO_KR_SERVICE_KEY is not set. Request a service key at "
        "data.go.kr and set it in the environment before running this script."
    )
RATE_PER_WORKER = 0.3  # seconds between calls per worker
_shutdown = False
_lock = __import__('threading').Lock()
_stats = {'probed': 0, 'found': 0, 'saved': 0, 'errors': 0}


def _signal_handler(sig, frame):
    global _shutdown
    logger.info("Shutdown requested...")
    _shutdown = True

signal.signal(signal.SIGINT, _signal_handler)


def get_existing_ids(db_path: str) -> set[str]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT chem_id FROM msds_details")
    ids = {r[0] for r in cur.fetchall()}
    conn.close()
    return ids


def probe_and_fetch(chem_id: str) -> list[tuple[str, int, str]]:
    """Probe one ID. If data exists, fetch all 16 sections. Returns list of (chem_id, sec, xml)."""
    results = []
    try:
        # Probe section 1
        r = requests.get(f"{BASE_URL}/getChemDetail01", params={
            "serviceKey": API_KEY, "chemId": chem_id
        }, timeout=10)

        if r.status_code != 200 or "<itemDetail>" not in r.text:
            return results

        # Found! Save section 1 and fetch rest
        results.append((chem_id, 1, r.text))

        for sec in range(2, 17):
            if _shutdown:
                break
            time.sleep(RATE_PER_WORKER)
            try:
                r2 = requests.get(f"{BASE_URL}/getChemDetail{sec:02d}", params={
                    "serviceKey": API_KEY, "chemId": chem_id
                }, timeout=10)
                if r2.status_code == 200 and "<itemDetail>" in r2.text:
                    results.append((chem_id, sec, r2.text))
                elif r2.status_code == 429:
                    logger.warning(f"Rate limited on {chem_id} sec {sec}, waiting 30s")
                    time.sleep(30)
            except Exception:
                pass

    except requests.RequestException as e:
        with _lock:
            _stats['errors'] += 1
    return results


def save_batch(db_path: str, items: list[tuple[str, int, str]]):
    """Save multiple sections to DB in one transaction."""
    if not items:
        return
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executemany(
        "INSERT OR REPLACE INTO msds_details (chem_id, section_no, xml_data) VALUES (?, ?, ?)",
        items
    )
    conn.commit()
    conn.close()


def process_id(chem_id: str, db_path: str):
    """Process one chemical ID: probe, fetch, save."""
    time.sleep(RATE_PER_WORKER)

    with _lock:
        _stats['probed'] += 1

    sections = probe_and_fetch(chem_id)
    if sections:
        save_batch(db_path, sections)
        with _lock:
            _stats['found'] += 1
            _stats['saved'] += len(sections)

    return len(sections) > 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=3740)
    parser.add_argument("--end", type=int, default=50000)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--db", default=DB_PATH)
    args = parser.parse_args()

    existing = get_existing_ids(args.db)
    logger.info(f"Existing: {len(existing)} chemicals")

    # Build candidate list
    candidates = [f"{i:06d}" for i in range(args.start, args.end + 1) if f"{i:06d}" not in existing]
    logger.info(f"Candidates: {len(candidates)} (range {args.start}-{args.end}, {args.workers} workers)")

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=args.workers, thread_name_prefix="w") as executor:
        futures = {}
        batch_size = 100

        for batch_start in range(0, len(candidates), batch_size):
            if _shutdown:
                break

            batch = candidates[batch_start:batch_start + batch_size]
            batch_futures = {
                executor.submit(process_id, cid, args.db): cid
                for cid in batch
            }
            futures.update(batch_futures)

            # Wait for batch to complete
            for future in as_completed(batch_futures):
                if _shutdown:
                    break
                future.result()  # propagate exceptions

            # Progress report
            elapsed = time.time() - start_time
            rate = _stats['probed'] / elapsed if elapsed > 0 else 0
            eta_h = (len(candidates) - _stats['probed']) / rate / 3600 if rate > 0 else 0
            logger.info(
                f"Progress: {_stats['probed']}/{len(candidates)} probed, "
                f"{_stats['found']} found, {_stats['saved']} sections saved, "
                f"{rate:.1f}/s, ETA: {eta_h:.1f}h"
            )

    elapsed = time.time() - start_time
    logger.info(f"\nDone: {_stats['probed']} probed, {_stats['found']} found, "
                f"{_stats['saved']} sections in {elapsed/60:.0f}min")

    # Final count
    conn = sqlite3.connect(args.db)
    total = conn.execute("SELECT COUNT(DISTINCT chem_id) FROM msds_details").fetchone()[0]
    conn.close()
    logger.info(f"DB total: {total} chemicals")


if __name__ == "__main__":
    main()

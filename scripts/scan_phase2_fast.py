"""
Phase 2 only: fetch remaining sections for already-discovered chemicals.
No probing needed — just fills in missing sections 2-16.

Workers: 32, rate limit: 0.1s per worker (safe within 100k/endpoint/day)
"""

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
API_KEY = "REDACTED_DATA_GO_KR_SERVICE_KEY"

_shutdown = False
_lock = __import__('threading').Lock()
_saved = 0

def _signal_handler(sig, frame):
    global _shutdown
    logger.info("Stopping...")
    _shutdown = True
signal.signal(signal.SIGINT, _signal_handler)


def get_incomplete_chemicals(db_path):
    """Find chemicals with < 16 sections."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT chem_id, GROUP_CONCAT(section_no) as have
        FROM msds_details
        GROUP BY chem_id
        HAVING COUNT(DISTINCT section_no) < 16
    """)
    result = []
    for cid, have_str in cur.fetchall():
        have = set(int(s) for s in have_str.split(',') if s.isdigit())
        missing = [s for s in range(1, 17) if s not in have]
        if missing:
            result.append((cid, missing))
    conn.close()
    return result


def fetch_one(chem_id, sec):
    """Fetch one section with polite rate limiting."""
    time.sleep(0.1)  # 0.1s per call per worker → ~10 workers = ~100 calls/s max
    try:
        r = requests.get(f"{BASE_URL}/getChemDetail{sec:02d}", params={
            "serviceKey": API_KEY, "chemId": chem_id
        }, timeout=10)
        if r.status_code == 200 and "<resultCode>00</resultCode>" in r.text:
            xml = r.text if "<itemDetail>" in r.text else None
            return (chem_id, sec, xml)
        if r.status_code == 429:
            logger.warning("Rate limited! Sleeping 60s...")
            time.sleep(60)
        return (chem_id, sec, None)
    except:
        return (chem_id, sec, None)


def main():
    work = get_incomplete_chemicals(DB_PATH)
    total_tasks = sum(len(missing) for _, missing in work)
    logger.info(f"Incomplete chemicals: {len(work)}, missing sections: {total_tasks}")

    if not work:
        logger.info("Nothing to do!")
        return

    # Build flat task list
    tasks = []
    for cid, missing in work:
        for sec in missing:
            tasks.append((cid, sec))

    global _saved
    batch = []
    start = time.time()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_one, cid, sec): (cid, sec) for cid, sec in tasks}

        for future in as_completed(futures):
            if _shutdown:
                break
            cid, sec, xml = future.result()
            if xml:
                batch.append((cid, sec, xml))

            # Save every 200
            if len(batch) >= 200:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("PRAGMA busy_timeout=30000")
                conn.execute("PRAGMA journal_mode=WAL")
                conn.executemany(
                    "INSERT OR REPLACE INTO msds_details (chem_id, section_no, xml_data) VALUES (?, ?, ?)",
                    batch
                )
                conn.commit()
                conn.close()
                _saved += len(batch)
                batch = []

                elapsed = time.time() - start
                rate = _saved / elapsed
                eta = (total_tasks - _saved) / rate / 60 if rate > 0 else 0
                logger.info(f"Saved: {_saved}/{total_tasks} ({rate:.0f}/s, ETA {eta:.0f}min)")

    # Final save
    if batch:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA busy_timeout=30000")
        conn.executemany(
            "INSERT OR REPLACE INTO msds_details (chem_id, section_no, xml_data) VALUES (?, ?, ?)",
            batch
        )
        conn.commit()
        conn.close()
        _saved += len(batch)

    elapsed = time.time() - start
    logger.info(f"Done: {_saved} sections in {elapsed/60:.0f}min")

    # Final count
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COUNT(DISTINCT chem_id) FROM msds_details").fetchone()[0]
    complete = conn.execute("SELECT COUNT(*) FROM (SELECT chem_id FROM msds_details GROUP BY chem_id HAVING COUNT(DISTINCT section_no) >= 15)").fetchone()[0]
    conn.close()
    logger.info(f"DB: {total} total, {complete} complete")


if __name__ == "__main__":
    main()

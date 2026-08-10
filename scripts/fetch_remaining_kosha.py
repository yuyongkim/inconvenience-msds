"""
Fetch remaining KOSHA MSDS chemicals from data.go.kr API.

Currently in DB: ~13,462 chemicals
KOSHA total: ~20,568 chemicals
Remaining: ~7,100 chemicals x 16 sections

Rate: 0.5s per call, 2 workers = ~1 call/0.25s effective
Daily limit: 100,000 per endpoint (운영계정)

Usage:
    python scripts/fetch_remaining_kosha.py                # full run
    python scripts/fetch_remaining_kosha.py --limit 50     # test 50 chemicals
    python scripts/fetch_remaining_kosha.py --dry-run      # show what would be fetched
"""

import argparse
import logging
import os
import signal
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = "G:/MSDS/data/terminology.db"
BASE_URL = "https://apis.data.go.kr/B552468/msdschem"
API_KEY = os.environ.get("DATA_GO_KR_SERVICE_KEY", "")
if not API_KEY:
    raise SystemExit(
        "DATA_GO_KR_SERVICE_KEY is not set. Request a service key at "
        "data.go.kr and set it in the environment before running this script."
    )
RATE_LIMIT = 0.5  # seconds between calls per worker
ALL_SECTIONS = list(range(1, 17))

_shutdown = False


def _signal_handler(sig, frame):
    global _shutdown
    logger.info("Shutdown requested, finishing current batch...")
    _shutdown = True

signal.signal(signal.SIGINT, _signal_handler)


# ------------------------------------------------------------------
# Step 1: Get full chemical list from API
# ------------------------------------------------------------------

def fetch_chem_list(page_size: int = 100) -> list[str]:
    """Fetch all chem_ids from KOSHA API."""
    all_ids = []
    page = 1

    while True:
        if _shutdown:
            break
        try:
            r = requests.get(f"{BASE_URL}/getChemList", params={
                "serviceKey": API_KEY,
                "numOfRows": page_size,
                "pageNo": page,
            }, timeout=15)

            if r.status_code != 200:
                logger.error(f"HTTP {r.status_code} on page {page}")
                break

            text = r.text
            if "<totalCount>0</totalCount>" in text and page > 1:
                break

            # Parse XML for chem IDs
            import re
            ids = re.findall(r'<chemId>(\d+)</chemId>', text)
            if not ids:
                # Try alternate field names
                ids = re.findall(r'<msdsMstSeq>(\d+)</msdsMstSeq>', text)
            if not ids:
                logger.info(f"No IDs found on page {page}, stopping")
                break

            all_ids.extend(ids)
            logger.info(f"Page {page}: {len(ids)} IDs (total: {len(all_ids)})")

            # Check if we got less than page_size = last page
            if len(ids) < page_size:
                break

            page += 1
            time.sleep(RATE_LIMIT)

        except Exception as e:
            logger.error(f"Error fetching page {page}: {e}")
            break

    return all_ids


# ------------------------------------------------------------------
# Step 2: Find missing chemicals
# ------------------------------------------------------------------

def get_existing_ids(db_path: str) -> set[str]:
    """Get chem_ids already in DB with all 16 sections."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT chem_id FROM msds_details
        GROUP BY chem_id
        HAVING COUNT(DISTINCT section_no) = 16
    """)
    ids = {r[0] for r in cur.fetchall()}
    conn.close()
    return ids


def get_all_existing_ids(db_path: str) -> set[str]:
    """Get all chem_ids in DB (even partial)."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT chem_id FROM msds_details")
    ids = {r[0] for r in cur.fetchall()}
    conn.close()
    return ids


# ------------------------------------------------------------------
# Step 3: Fetch sections
# ------------------------------------------------------------------

def fetch_section(chem_id: str, section_no: int) -> str | None:
    """Fetch one MSDS section. Returns XML or None."""
    url = f"{BASE_URL}/getChemDetail{section_no:02d}"
    try:
        r = requests.get(url, params={
            "serviceKey": API_KEY,
            "chemId": chem_id,
        }, timeout=15)

        if r.status_code == 200 and "<resultCode>00</resultCode>" in r.text:
            if "<itemDetail>" in r.text:
                return r.text
            return None  # success but empty
        elif r.status_code == 429:
            logger.warning("Rate limited! Waiting 60s...")
            time.sleep(60)
            return None
        else:
            return None
    except Exception as e:
        logger.debug(f"Error {chem_id} sec {section_no}: {e}")
        return None


def save_section(db_path: str, chem_id: str, section_no: int, xml_data: str):
    """Save one section to DB."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("""
        INSERT OR REPLACE INTO msds_details (chem_id, section_no, xml_data)
        VALUES (?, ?, ?)
    """, (chem_id, section_no, xml_data))
    conn.commit()
    conn.close()


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Fetch remaining KOSHA MSDS data")
    parser.add_argument("--limit", type=int, default=0, help="Max chemicals to process (0=all)")
    parser.add_argument("--workers", type=int, default=2, help="Parallel workers")
    parser.add_argument("--dry-run", action="store_true", help="Just show counts, don't fetch")
    parser.add_argument("--db", default=DB_PATH)
    args = parser.parse_args()

    # Check what we have
    existing_complete = get_existing_ids(args.db)
    existing_any = get_all_existing_ids(args.db)
    logger.info(f"DB: {len(existing_complete)} complete, {len(existing_any)} total")

    # Get full list from API
    logger.info("Fetching chemical list from API...")
    api_ids = fetch_chem_list()

    if not api_ids:
        # Fallback: use KOSHA IDs from chemical_terms table
        logger.info("API list empty, using chemical_terms KOSHA_IDs as fallback")
        conn = sqlite3.connect(args.db)
        cur = conn.cursor()
        cur.execute("SELECT description FROM chemical_terms WHERE description LIKE 'KOSHA_ID:%'")
        api_ids = [r[0].split(":")[1] for r in cur.fetchall()]
        conn.close()

    logger.info(f"Total known IDs: {len(api_ids)}")

    # Find missing
    missing = [cid for cid in api_ids if cid not in existing_complete]
    logger.info(f"Missing (incomplete): {len(missing)}")

    if args.dry_run:
        logger.info("Dry run — exiting")
        return

    if args.limit > 0:
        missing = missing[:args.limit]

    if not missing:
        logger.info("Nothing to fetch!")
        return

    # Fetch missing sections
    total_calls = 0
    total_saved = 0
    start_time = time.time()

    for idx, chem_id in enumerate(missing):
        if _shutdown:
            break

        # Check which sections are missing for this chemical
        conn = sqlite3.connect(args.db)
        cur = conn.cursor()
        cur.execute("SELECT section_no FROM msds_details WHERE chem_id=?", (chem_id,))
        have = {r[0] for r in cur.fetchall()}
        conn.close()

        need = [s for s in ALL_SECTIONS if s not in have]
        if not need:
            continue

        for sec_no in need:
            if _shutdown:
                break

            xml_data = fetch_section(chem_id, sec_no)
            total_calls += 1

            if xml_data:
                save_section(args.db, chem_id, sec_no, xml_data)
                total_saved += 1

            time.sleep(RATE_LIMIT)

        if (idx + 1) % 10 == 0:
            elapsed = time.time() - start_time
            rate = total_calls / elapsed if elapsed > 0 else 0
            logger.info(
                f"Progress: {idx+1}/{len(missing)} chemicals, "
                f"{total_calls} calls, {total_saved} saved, "
                f"{rate:.1f} calls/s"
            )

    elapsed = time.time() - start_time
    logger.info(f"\nDone: {total_calls} calls, {total_saved} saved in {elapsed:.0f}s")


if __name__ == "__main__":
    main()

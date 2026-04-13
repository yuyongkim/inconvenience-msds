"""
Fill chemicals that only have section 1 (from Phase 1 probe).
Fetch sections 2-16 for these.
"""

import logging
import signal
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger()

DB = "G:/MSDS/data/terminology.db"
URL = "https://apis.data.go.kr/B552468/msdschem"
KEY = "REDACTED_DATA_GO_KR_SERVICE_KEY"

stop = False
def _sig(s, f): global stop; stop = True; log.info("Stopping...")
signal.signal(signal.SIGINT, _sig)


_consecutive_429 = 0
_429_lock = __import__('threading').Lock()

def fetch(cid, sec):
    global _consecutive_429, stop
    time.sleep(0.05)
    try:
        r = requests.get(f"{URL}/getChemDetail{sec:02d}",
                         params={"serviceKey": KEY, "chemId": cid}, timeout=10)
        if r.status_code == 200 and "<resultCode>00</resultCode>" in r.text:
            with _429_lock:
                _consecutive_429 = 0
            return (cid, sec, r.text if "<itemDetail>" in r.text else None)
        if r.status_code == 429:
            with _429_lock:
                _consecutive_429 += 1
                if _consecutive_429 >= 20:
                    log.warning(f"429 x{_consecutive_429}! pausing 10min...")
                    time.sleep(600)
                    _consecutive_429 = 0
                else:
                    log.warning(f"429 x{_consecutive_429}, sleeping 120s")
                    time.sleep(120)
    except:
        pass
    return (cid, sec, None)


def save(items):
    if not items:
        return 0
    real = [(c, s, x) for c, s, x in items if x]
    c = sqlite3.connect(DB)
    c.execute("PRAGMA busy_timeout=30000")
    c.execute("PRAGMA journal_mode=WAL")
    # Save even empty results to mark as "checked"
    c.executemany("INSERT OR REPLACE INTO msds_details (chem_id, section_no, xml_data) VALUES (?,?,?)",
                  [(cid, sec, xml or '<empty/>') for cid, sec, xml in items])
    c.commit()
    c.close()
    return len(real)


def main():
    # Get chemicals with only 1-2 sections
    c = sqlite3.connect(DB)
    rows = c.execute("""
        SELECT chem_id FROM msds_details
        GROUP BY chem_id HAVING COUNT(DISTINCT section_no) <= 2
    """).fetchall()
    c.close()
    chem_ids = [r[0] for r in rows]
    log.info(f"Chemicals with <=2 sections: {len(chem_ids)}")

    total_saved = 0
    start = time.time()
    batch_size = 100  # 100 chemicals × 15 sections = 1500 calls per batch

    for i in range(0, len(chem_ids), batch_size):
        if stop:
            break
        batch_cids = chem_ids[i:i + batch_size]

        # Build tasks: sections 2-16 for each
        tasks = [(cid, sec) for cid in batch_cids for sec in range(2, 17)]

        results = []
        with ThreadPoolExecutor(max_workers=20) as ex:
            futs = {ex.submit(fetch, cid, sec): (cid, sec) for cid, sec in tasks}
            for f in as_completed(futs):
                if stop: break
                results.append(f.result())

        real = save(results)
        total_saved += real
        elapsed = time.time() - start
        rate = total_saved / elapsed if elapsed > 0 else 0
        done = i + len(batch_cids)

        c = sqlite3.connect(DB)
        complete = c.execute("SELECT COUNT(*) FROM (SELECT chem_id FROM msds_details GROUP BY chem_id HAVING COUNT(DISTINCT section_no)>=15)").fetchone()[0]
        c.close()

        log.info(f"[{done}/{len(chem_ids)}] +{real} real sections | "
                 f"Total: {total_saved} | Complete: {complete:,} | {rate:.1f}/s")

    elapsed = time.time() - start
    log.info(f"Done: {total_saved} sections in {elapsed/60:.0f}min")


if __name__ == "__main__":
    main()

"""
Phase 2: Fetch missing sections in small batches.
No memory issues — processes 50 chemicals at a time.
10 workers, 0.1s delay per call.
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


def fetch(cid, sec):
    time.sleep(0.1)
    try:
        r = requests.get(f"{URL}/getChemDetail{sec:02d}",
                         params={"serviceKey": KEY, "chemId": cid}, timeout=10)
        if r.status_code == 200 and "<itemDetail>" in r.text:
            return (cid, sec, r.text)
        if r.status_code == 429:
            log.warning("429! sleeping 60s")
            time.sleep(60)
    except:
        pass
    return (cid, sec, None)


def get_batch(n=50):
    """Get next batch of incomplete chemicals."""
    c = sqlite3.connect(DB)
    rows = c.execute("""
        SELECT chem_id, GROUP_CONCAT(section_no) FROM msds_details
        GROUP BY chem_id HAVING COUNT(DISTINCT section_no) < 16
        LIMIT ?
    """, (n,)).fetchall()
    c.close()
    tasks = []
    for cid, have in rows:
        have_set = set(int(s) for s in have.split(',') if s.isdigit())
        for s in range(1, 17):
            if s not in have_set:
                tasks.append((cid, s))
    return tasks


def save(items):
    if not items:
        return
    c = sqlite3.connect(DB)
    c.execute("PRAGMA busy_timeout=30000")
    c.execute("PRAGMA journal_mode=WAL")
    c.executemany("INSERT OR REPLACE INTO msds_details (chem_id, section_no, xml_data) VALUES (?,?,?)", items)
    c.commit()
    c.close()


def main():
    total_saved = 0
    start = time.time()

    while not stop:
        tasks = get_batch(50)
        if not tasks:
            log.info("All done!")
            break

        batch = []
        with ThreadPoolExecutor(max_workers=10) as ex:
            futs = {ex.submit(fetch, cid, sec): (cid, sec) for cid, sec in tasks}
            for f in as_completed(futs):
                if stop: break
                cid, sec, xml = f.result()
                if xml:
                    batch.append((cid, sec, xml))

        save(batch)
        total_saved += len(batch)
        elapsed = time.time() - start
        rate = total_saved / elapsed if elapsed > 0 else 0

        c = sqlite3.connect(DB)
        complete = c.execute("SELECT COUNT(*) FROM (SELECT chem_id FROM msds_details GROUP BY chem_id HAVING COUNT(DISTINCT section_no)>=15)").fetchone()[0]
        c.close()

        log.info(f"Batch done: +{len(batch)} | Total saved: {total_saved} | "
                 f"Complete: {complete:,} | Rate: {rate:.1f}/s")

    elapsed = time.time() - start
    log.info(f"Finished: {total_saved} sections in {elapsed/60:.0f}min")


if __name__ == "__main__":
    main()

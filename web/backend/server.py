"""
Braille MSDS Web Service.

FastAPI backend serving Korean chemical MSDS in braille format.

Endpoints:
    GET /                           → serve frontend
    GET /api/chemicals              → search/list chemicals
    GET /api/chemicals/{chem_id}    → chemical detail with all 16 sections
    GET /api/chemicals/{chem_id}/braille → Korean text + braille
    GET /api/chemicals/{chem_id}/braille.brf → BRF file download
    GET /api/chemicals/{chem_id}/braille.txt → Unicode braille download
    POST /api/bulk-jobs             → create bulk ZIP export job
    GET /api/bulk-jobs/{job_id}     → poll bulk ZIP export status
    GET /api/bulk-jobs/{job_id}/download → download finished bulk ZIP
    GET /api/stats                  → DB statistics
    GET /api/ingredient-presets     → worked examples for the preview tab
    POST /api/ingredient-summary    → restructure an ingredient list, in braille

Run:
    cd web/backend
    uvicorn server:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations
import csv
import io
import json
import os
import re
import sqlite3
import sys
import threading
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from lxml import etree

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.ko_braille import encode_korean_braille
from pipeline.ingredient_summary import (
    parse_list as parse_ingredient_list,
    summarize as summarize_ingredients,
)

FRONTEND_DIR = PROJECT_ROOT / "web" / "frontend"


def _resolve_db_path() -> Path | None:
    env = (
        os.getenv("BRAILLE_MSDS_DB_PATH")
        or os.getenv("BRAILLE_DB_PATH")
        or os.getenv("DB_PATH")
    )
    if env:
        return Path(env).expanduser()

    candidates = [
        PROJECT_ROOT / "data" / "terminology.db",
        PROJECT_ROOT / "data" / "terminology.sample.db",
        PROJECT_ROOT / "terminology.db",
        Path.cwd() / "terminology.db",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


DB_PATH = _resolve_db_path()
BULK_JOB_DIR = PROJECT_ROOT / ".gstack" / "bulk-jobs"
BULK_JOB_DIR.mkdir(parents=True, exist_ok=True)
BULK_JOBS: dict[str, dict] = {}
BULK_JOBS_LOCK = threading.Lock()
ALLOWED_BULK_FORMATS = {"txt", "brf"}
MAX_BULK_ITEMS = 250

app = FastAPI(
    title="Braille MSDS",
    description="Korean chemical safety data in braille format",
    version="1.0.0",
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Section titles
# ---------------------------------------------------------------------------

SECTION_TITLES = {
    1: '화학제품과 회사에 관한 정보',
    2: '유해성·위험성',
    3: '구성성분의 명칭 및 함유량',
    4: '응급조치 요령',
    5: '폭발·화재시 대처방법',
    6: '누출사고시 대처방법',
    7: '취급 및 저장방법',
    8: '노출방지 및 개인보호구',
    9: '물리화학적 특성',
    10: '안정성 및 반응성',
    11: '독성에 관한 정보',
    12: '환경에 미치는 영향',
    13: '폐기시 주의사항',
    14: '운송에 필요한 정보',
    15: '법적 규제현황',
    16: '그 밖의 참고사항',
}


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _connect_db() -> sqlite3.Connection:
    if DB_PATH is None or not DB_PATH.exists():
        raise RuntimeError("terminology.db not found. Set BRAILLE_MSDS_DB_PATH to the DB file path.")

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def get_db() -> sqlite3.Connection:
    try:
        return _connect_db()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# GHS 그림문자 코드 → 한국어 의미 (시각장애인용)
GHS_PICTOGRAMS = {
    'GHS01': '폭발성',
    'GHS02': '인화성',
    'GHS03': '산화성',
    'GHS04': '고압가스',
    'GHS05': '부식성',
    'GHS06': '급성독성',
    'GHS07': '경고(피부자극/호흡기자극)',
    'GHS08': '건강유해성(발암성/생식독성)',
    'GHS09': '수생환경유해성',
}


def _convert_ghs_pictograms(text: str) -> str:
    """Convert GHS image filenames to Korean pictogram meanings."""
    import re
    # Replace GHS##.gif with Korean meaning
    def repl(m):
        code = m.group(1)
        return GHS_PICTOGRAMS.get(code, code)
    return re.sub(r'(GHS\d{2})\.gif', repl, text)


def _clean_msds_text(label: str, detail: str) -> str:
    """Clean MSDS text for braille output."""
    import re
    # Special handling for 그림문자 field
    if '그림문자' in label:
        # Convert GHS##.gif|GHS##.gif → comma-separated Korean meanings
        parts = detail.split('|')
        meanings = []
        for part in parts:
            part = part.strip()
            m = re.match(r'(GHS\d{2})(?:\.gif)?', part)
            if m:
                code = m.group(1)
                meanings.append(GHS_PICTOGRAMS.get(code, code))
            elif part:
                meanings.append(part)
        return ', '.join(meanings)

    # General cleanup: remove .gif references
    detail = _convert_ghs_pictograms(detail)

    # Replace | with comma for readability
    detail = detail.replace('|', ', ')

    return detail


def extract_section_text(xml_data: str) -> str:
    """Extract Korean text from MSDS section XML, cleaned for braille."""
    if not xml_data or xml_data == '<empty/>':
        return ''
    try:
        root = etree.fromstring(xml_data.encode('utf-8'))
        parts = []
        for item in root.findall('.//item'):
            label = item.findtext('msdsItemNameKor', '')
            detail = item.findtext('itemDetail', '')
            if detail and detail != '자료없음':
                cleaned = _clean_msds_text(label, detail)
                if label:
                    parts.append(f"{label}: {cleaned}")
                else:
                    parts.append(cleaned)
        return '\n'.join(parts)
    except Exception:
        return ''


def get_chemical_name(conn: sqlite3.Connection, chem_id: str) -> Optional[str]:
    """Get chemical name from section 1."""
    row = conn.execute(
        "SELECT xml_data FROM msds_details WHERE chem_id = ? AND section_no = 1",
        (chem_id,)
    ).fetchone()
    if not row:
        return None
    try:
        root = etree.fromstring(row['xml_data'].encode('utf-8'))
        for item in root.findall('.//item'):
            if item.findtext('msdsItemCode', '') == 'A02':
                name = item.findtext('itemDetail', '')
                return name if name and name != '자료없음' else None
    except Exception:
        pass
    return None


def build_full_msds_text(conn: sqlite3.Connection, chem_id: str) -> dict:
    """Build complete Korean MSDS text for a chemical."""
    rows = conn.execute(
        "SELECT section_no, xml_data FROM msds_details WHERE chem_id = ? ORDER BY section_no",
        (chem_id,)
    ).fetchall()

    if not rows:
        return None

    sections = {}
    for row in rows:
        text = extract_section_text(row['xml_data'])
        if text:
            sections[row['section_no']] = text

    name = get_chemical_name(conn, chem_id)

    return {
        'chem_id': chem_id,
        'name': name or '(이름 없음)',
        'sections': sections,
    }


def build_korean_msds_document(msds: dict) -> str:
    parts = [f"물질안전보건자료: {msds['name']}"]
    for sec_no in range(1, 17):
        if sec_no in msds['sections']:
            title = SECTION_TITLES.get(sec_no, f'섹션 {sec_no}')
            parts.append(f"\n{sec_no}. {title}")
            parts.append(msds['sections'][sec_no])
    return '\n'.join(parts)


def build_braille_export(conn: sqlite3.Connection, chem_id: str) -> dict | None:
    msds = build_full_msds_text(conn, chem_id)
    if not msds:
        return None

    korean_text = build_korean_msds_document(msds)
    braille = encode_korean_braille(korean_text)

    return {
        'chem_id': msds['chem_id'],
        'name': msds['name'],
        'korean_text': korean_text,
        'braille': braille,
        'sections': msds['sections'],
        'stats': {
            'korean_chars': len(korean_text),
            'braille_cells': len(braille),
        },
    }


def build_brf_text(braille: str) -> str:
    from pipeline.embosser import unicode_to_brf

    return unicode_to_brf(braille)


def safe_filename_part(text: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', ' ', text).strip()
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned[:80] or "unnamed"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_public_bulk_job(job: dict) -> dict:
    return {
        'job_id': job['job_id'],
        'status': job['status'],
        'created_at': job['created_at'],
        'completed_at': job.get('completed_at'),
        'formats': job['formats'],
        'total_items': job['total_items'],
        'completed_items': job['completed_items'],
        'failed_items': job['failed_items'],
        'download_url': job.get('download_url'),
        'error': job.get('error'),
    }


def update_bulk_job(job_id: str, **patch) -> dict:
    with BULK_JOBS_LOCK:
        job = BULK_JOBS[job_id]
        job.update(patch)
        return dict(job)


def create_bulk_zip_job(job_id: str, chem_ids: list[str], formats: list[str]) -> None:
    job_dir = BULK_JOB_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    zip_path = job_dir / "braille-bulk.zip"
    items: list[dict] = []
    conn: sqlite3.Connection | None = None

    update_bulk_job(job_id, status="running", error=None)

    try:
        conn = _connect_db()
        with conn:
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                summary_io = io.StringIO()
                summary = csv.writer(summary_io)
                summary.writerow(["chem_id", "name", "status", "txt_path", "brf_path", "korean_chars", "braille_cells", "error"])

                for index, chem_id in enumerate(chem_ids, start=1):
                    item = {
                        "chem_id": chem_id,
                        "status": "failed",
                        "txt_path": "",
                        "brf_path": "",
                        "error": "",
                    }
                    try:
                        export = build_braille_export(conn, chem_id)
                        if not export:
                            raise ValueError("Chemical not found")

                        base_name = f"{export['chem_id']}_{safe_filename_part(export['name'])}"
                        item["name"] = export["name"]
                        item["status"] = "done"

                        if "txt" in formats:
                            txt_path = f"txt/{base_name}.txt"
                            archive.writestr(txt_path, export["braille"])
                            item["txt_path"] = txt_path

                        if "brf" in formats:
                            brf_path = f"brf/{base_name}.brf"
                            archive.writestr(brf_path, build_brf_text(export["braille"]))
                            item["brf_path"] = brf_path

                        item["korean_chars"] = export["stats"]["korean_chars"]
                        item["braille_cells"] = export["stats"]["braille_cells"]
                    except Exception as exc:
                        item["name"] = item.get("name", "")
                        item["error"] = str(exc)
                    items.append(item)
                    summary.writerow([
                        item["chem_id"],
                        item.get("name", ""),
                        item["status"],
                        item["txt_path"],
                        item["brf_path"],
                        item.get("korean_chars", 0),
                        item.get("braille_cells", 0),
                        item["error"],
                    ])

                    done_count = sum(1 for row in items if row["status"] == "done")
                    failed_count = sum(1 for row in items if row["status"] != "done")
                    update_bulk_job(
                        job_id,
                        completed_items=done_count,
                        failed_items=failed_count,
                    )

                manifest = {
                    "job_id": job_id,
                    "generated_at": utc_now_iso(),
                    "formats": formats,
                    "items": items,
                }
                archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
                archive.writestr("summary.csv", summary_io.getvalue())
    except Exception as exc:
        update_bulk_job(
            job_id,
            status="failed",
            error=str(exc),
            completed_at=utc_now_iso(),
        )
        return
    finally:
        if conn is not None:
            conn.close()

    update_bulk_job(
        job_id,
        status="done",
        completed_at=utc_now_iso(),
        download_path=str(zip_path),
        download_url=f"/api/bulk-jobs/{job_id}/download",
    )


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.get("/api/stats")
def get_stats():
    """Database statistics."""
    conn = get_db()
    total = conn.execute("SELECT COUNT(DISTINCT chem_id) FROM msds_details").fetchone()[0]
    complete = conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT chem_id FROM msds_details
            GROUP BY chem_id HAVING COUNT(DISTINCT section_no) >= 15
        )
    """).fetchone()[0]
    sections = conn.execute("SELECT COUNT(*) FROM msds_details").fetchone()[0]
    conn.close()
    return {
        'total_chemicals': total,
        'complete_chemicals': complete,
        'total_sections': sections,
    }


@app.get("/api/chemicals")
def list_chemicals(
    search: Optional[str] = Query(None, description="Search by Korean name"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List or search chemicals."""
    conn = get_db()

    # Get chemicals with their names
    query = """
        SELECT DISTINCT chem_id, xml_data
        FROM msds_details
        WHERE section_no = 1
        ORDER BY chem_id
    """
    all_rows = conn.execute(query).fetchall()
    conn.close()

    results = []
    for row in all_rows:
        name = ''
        try:
            root = etree.fromstring(row['xml_data'].encode('utf-8'))
            for item in root.findall('.//item'):
                if item.findtext('msdsItemCode', '') == 'A02':
                    n = item.findtext('itemDetail', '')
                    if n and n != '자료없음':
                        name = n
                    break
        except Exception:
            pass

        if not name:
            continue

        if search and search.lower() not in name.lower():
            continue

        results.append({
            'chem_id': row['chem_id'],
            'name': name,
        })

    total_count = len(results)
    paged = results[offset:offset + limit]

    return {
        'total': total_count,
        'offset': offset,
        'limit': limit,
        'results': paged,
    }


@app.get("/api/chemicals/{chem_id}")
def get_chemical(chem_id: str):
    """Get chemical MSDS with all 16 sections."""
    conn = get_db()
    msds = build_full_msds_text(conn, chem_id)
    conn.close()

    if not msds:
        raise HTTPException(status_code=404, detail="Chemical not found")

    # Structure sections by title
    structured = []
    for sec_no in range(1, 17):
        if sec_no in msds['sections']:
            structured.append({
                'section_no': sec_no,
                'title': SECTION_TITLES.get(sec_no, f'섹션 {sec_no}'),
                'text': msds['sections'][sec_no],
            })

    return {
        'chem_id': msds['chem_id'],
        'name': msds['name'],
        'sections': structured,
    }


@app.get("/api/chemicals/{chem_id}/braille")
def get_braille(chem_id: str):
    """Get chemical MSDS as Korean braille."""
    conn = get_db()
    export = build_braille_export(conn, chem_id)
    conn.close()

    if not export:
        raise HTTPException(status_code=404, detail="Chemical not found")

    # Structured sections (text + braille per section)
    structured = []
    for sec_no in range(1, 17):
        if sec_no in export['sections']:
            sec_text = export['sections'][sec_no]
            structured.append({
                'section_no': sec_no,
                'title': SECTION_TITLES.get(sec_no, f'섹션 {sec_no}'),
                'korean': sec_text,
                'braille': encode_korean_braille(sec_text),
            })

    return {
        'chem_id': export['chem_id'],
        'name': export['name'],
        'korean_text': export['korean_text'],
        'braille': export['braille'],
        'sections': structured,
        'stats': export['stats'],
    }


@app.get("/api/chemicals/{chem_id}/braille.txt")
def download_braille_txt(chem_id: str):
    """Download braille as UTF-8 text file (Unicode braille)."""
    conn = get_db()
    export = build_braille_export(conn, chem_id)
    conn.close()

    if not export:
        raise HTTPException(status_code=404, detail="Chemical not found")

    return PlainTextResponse(
        content=export['braille'],
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{chem_id}_braille.txt"'
        }
    )


@app.get("/api/chemicals/{chem_id}/braille.brf")
def download_braille_brf(chem_id: str):
    """Download braille as BRF file for embossers."""
    conn = get_db()
    export = build_braille_export(conn, chem_id)
    conn.close()

    if not export:
        raise HTTPException(status_code=404, detail="Chemical not found")

    return PlainTextResponse(
        content=build_brf_text(export['braille']),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{chem_id}_braille.brf"'
        }
    )


@app.post("/api/bulk-jobs", status_code=202)
def create_bulk_job(request: dict, background_tasks: BackgroundTasks):
    """Create a bulk export job and return a polling handle."""
    raw_ids = request.get("chem_ids", [])
    raw_formats = request.get("formats", ["txt", "brf"])

    if not isinstance(raw_ids, list):
        raise HTTPException(status_code=400, detail="chem_ids must be a list")
    if not isinstance(raw_formats, list):
        raise HTTPException(status_code=400, detail="formats must be a list")

    chem_ids: list[str] = []
    seen_ids: set[str] = set()
    for raw in raw_ids:
        chem_id = str(raw).strip()
        if not chem_id or chem_id in seen_ids:
            continue
        seen_ids.add(chem_id)
        chem_ids.append(chem_id)

    formats = [str(value).strip().lower() for value in raw_formats if str(value).strip()]
    invalid_formats = [value for value in formats if value not in ALLOWED_BULK_FORMATS]

    if not chem_ids:
        raise HTTPException(status_code=400, detail="At least one chem_id is required")
    if len(chem_ids) > MAX_BULK_ITEMS:
        raise HTTPException(status_code=400, detail=f"Bulk export supports up to {MAX_BULK_ITEMS} items")
    if not formats:
        raise HTTPException(status_code=400, detail="At least one format is required")
    if invalid_formats:
        raise HTTPException(status_code=400, detail=f"Unsupported formats: {', '.join(invalid_formats)}")

    job_id = uuid4().hex[:12]
    job = {
        "job_id": job_id,
        "status": "queued",
        "created_at": utc_now_iso(),
        "completed_at": None,
        "formats": formats,
        "total_items": len(chem_ids),
        "completed_items": 0,
        "failed_items": 0,
        "download_path": None,
        "download_url": None,
        "error": None,
    }

    with BULK_JOBS_LOCK:
        BULK_JOBS[job_id] = job

    background_tasks.add_task(create_bulk_zip_job, job_id, chem_ids, formats)
    return get_public_bulk_job(job)


@app.get("/api/bulk-jobs/{job_id}")
def get_bulk_job(job_id: str):
    """Return the current status of a bulk export job."""
    with BULK_JOBS_LOCK:
        job = BULK_JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Bulk job not found")
        return get_public_bulk_job(job)


@app.get("/api/bulk-jobs/{job_id}/download")
def download_bulk_job(job_id: str):
    """Download the generated bulk ZIP once the job completes."""
    with BULK_JOBS_LOCK:
        job = BULK_JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Bulk job not found")
        if job["status"] != "done" or not job.get("download_path"):
            raise HTTPException(status_code=409, detail="Bulk job is not ready for download")
        download_path = Path(job["download_path"])

    if not download_path.exists():
        raise HTTPException(status_code=404, detail="Bulk archive not found")

    return FileResponse(
        path=str(download_path),
        media_type="application/zip",
        filename=f"braille-bulk-{job_id}.zip",
    )


# ---------------------------------------------------------------------------
# Ingredient preview
# ---------------------------------------------------------------------------

# Worked examples, so a first-time visitor can see what the summariser does
# without having a bottle to hand. These are illustrative ingredient lists in
# the form Korean labels print, not transcriptions of any company's product,
# and the labels say so. Every name is a standardised entry from the Korean
# Cosmetic Association dictionary.
INGREDIENT_PRESETS = [
    {
        "id": "cream",
        "label_ko": "예시 · 수분 크림",
        "label_en": "Example · moisturising cream",
        "text": ("정제수, 글리세린, 나이아신아마이드, 부틸렌글라이콜, 스쿠알레인, "
                 "세테아릴알코올, 판테놀, 리날룰, 제라니올, 소듐하이알루로네이트, "
                 "다이소듐이디티에이, 토코페롤"),
    },
    {
        "id": "shampoo",
        "label_ko": "예시 · 샴푸",
        "label_en": "Example · shampoo",
        "text": ("정제수, 소듐라우레스설페이트, 코카미도프로필베타인, 글리세린, "
                 "다이메티콘, 시트릭애씨드, 참나무이끼추출물, 헥실신남알, 리모넨, "
                 "소듐클로라이드, 판테놀"),
    },
    {
        "id": "lipbalm",
        "label_ko": "예시 · 립밤",
        "label_en": "Example · lip balm",
        "text": ("피마자씨오일, 칸데릴라왁스, 밀납, 시어버터, 토코페릴아세테이트, "
                 "쿠마린, 벤질살리실레이트, 아이소유제놀"),
    },
    {
        "id": "chemical",
        "label_ko": "예시 · 화학물질명",
        "label_en": "Example · chemical names",
        "text": "다이메틸설폭사이드, 소듐하이드록사이드, 트라이클로로에틸렌, 아세톤",
    },
]


@app.get("/api/ingredient-presets")
def ingredient_presets():
    """Worked examples for the preview tab, so the page has something to show."""
    return {"presets": INGREDIENT_PRESETS}


@app.post("/api/ingredient-summary")
async def ingredient_summary(request: dict):
    """Restructure an ingredient list and render the summary in braille.

    Reports what the label states and what labelling rules single out. It does
    not assess safety, and the summary text says so in its closing line rather
    than relying on a disclaimer elsewhere on the page.
    """
    text = (request.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    if len(text) > 4000:
        raise HTTPException(status_code=400, detail="Text too long (max 4,000 chars)")

    items = parse_ingredient_list(text)
    if not items:
        raise HTTPException(status_code=400, detail="Could not read an ingredient list")

    summary = summarize_ingredients(text)
    braille = encode_korean_braille(summary)
    return {
        "summary": summary,
        "braille": braille,
        "braille_cells": len(braille),
        "count": len(items),
        "allergens": [
            {"name": i.name, "english": i.labelled_allergen}
            for i in items if i.labelled_allergen
        ],
        "ingredients": [
            {
                "name": i.name,
                "position": i.position + 1,
                "band": i.share_band,
                "allergen": i.labelled_allergen,
                "roots": i.roots,
            }
            for i in items
        ],
    }


@app.post("/api/convert")
async def convert_text(request: dict):
    """Real-time Korean text → braille conversion."""
    text = request.get('text', '')
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    if len(text) > 50000:
        raise HTTPException(status_code=400, detail="Text too long (max 50,000 chars)")

    braille = encode_korean_braille(text)
    return {
        'text': text,
        'braille': braille,
        'text_chars': len(text),
        'braille_cells': len(braille),
    }


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def serve_index():
    """Serve frontend index.html."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding='utf-8'))
    return HTMLResponse("<h1>Frontend not found</h1><p>Build frontend first.</p>")


# Mount static files if frontend dir exists
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

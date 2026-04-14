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
    GET /api/stats                  → DB statistics

Run:
    cd web/backend
    uvicorn server:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations
import os
import sqlite3
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from lxml import etree

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.ko_braille import encode_korean_braille

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
        PROJECT_ROOT / "terminology.db",
        Path.cwd() / "terminology.db",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


DB_PATH = _resolve_db_path()

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

def get_db() -> sqlite3.Connection:
    if DB_PATH is None or not DB_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="terminology.db not found. Set BRAILLE_MSDS_DB_PATH to the DB file path.",
        )

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


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
    msds = build_full_msds_text(conn, chem_id)
    conn.close()

    if not msds:
        raise HTTPException(status_code=404, detail="Chemical not found")

    # Build full text
    parts = [f"물질안전보건자료: {msds['name']}"]
    for sec_no in range(1, 17):
        if sec_no in msds['sections']:
            title = SECTION_TITLES.get(sec_no, f'섹션 {sec_no}')
            parts.append(f"\n{sec_no}. {title}")
            parts.append(msds['sections'][sec_no])

    korean_text = '\n'.join(parts)
    braille = encode_korean_braille(korean_text)

    # Structured sections (text + braille per section)
    structured = []
    for sec_no in range(1, 17):
        if sec_no in msds['sections']:
            sec_text = msds['sections'][sec_no]
            structured.append({
                'section_no': sec_no,
                'title': SECTION_TITLES.get(sec_no, f'섹션 {sec_no}'),
                'korean': sec_text,
                'braille': encode_korean_braille(sec_text),
            })

    return {
        'chem_id': msds['chem_id'],
        'name': msds['name'],
        'korean_text': korean_text,
        'braille': braille,
        'sections': structured,
        'stats': {
            'korean_chars': len(korean_text),
            'braille_cells': len(braille),
        },
    }


@app.get("/api/chemicals/{chem_id}/braille.txt")
def download_braille_txt(chem_id: str):
    """Download braille as UTF-8 text file (Unicode braille)."""
    conn = get_db()
    msds = build_full_msds_text(conn, chem_id)
    conn.close()

    if not msds:
        raise HTTPException(status_code=404, detail="Chemical not found")

    parts = [f"물질안전보건자료: {msds['name']}"]
    for sec_no in range(1, 17):
        if sec_no in msds['sections']:
            title = SECTION_TITLES.get(sec_no, f'섹션 {sec_no}')
            parts.append(f"\n{sec_no}. {title}")
            parts.append(msds['sections'][sec_no])

    korean_text = '\n'.join(parts)
    braille = encode_korean_braille(korean_text)

    return PlainTextResponse(
        content=braille,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{chem_id}_braille.txt"'
        }
    )


@app.get("/api/chemicals/{chem_id}/braille.brf")
def download_braille_brf(chem_id: str):
    """Download braille as BRF file for embossers."""
    from pipeline.embosser import unicode_to_brf

    conn = get_db()
    msds = build_full_msds_text(conn, chem_id)
    conn.close()

    if not msds:
        raise HTTPException(status_code=404, detail="Chemical not found")

    parts = [f"물질안전보건자료: {msds['name']}"]
    for sec_no in range(1, 17):
        if sec_no in msds['sections']:
            title = SECTION_TITLES.get(sec_no, f'섹션 {sec_no}')
            parts.append(f"\n{sec_no}. {title}")
            parts.append(msds['sections'][sec_no])

    korean_text = '\n'.join(parts)
    braille = encode_korean_braille(korean_text)
    brf = unicode_to_brf(braille)

    return PlainTextResponse(
        content=brf,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{chem_id}_braille.brf"'
        }
    )


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

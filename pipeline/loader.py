"""
Braille file loaders.

Supports:
  - BRF (ASCII-based Braille Ready Format)
  - Unicode braille (UTF-8 text with U+2800-U+28FF characters)
"""

from __future__ import annotations
from pathlib import Path


def load_brf(file_path: str) -> dict:
    """
    Load a BRF file and return structured data.

    BRF uses ASCII encoding. Page breaks are form feed (0x0C).

    Returns:
        {
            "format": "brf",
            "raw_lines": [...],
            "pages": [ {"page_num": 1, "lines": [...]} ],
            "metadata": {"filename": "...", "total_lines": N, "total_pages": N}
        }
    """
    path = Path(file_path)
    content = path.read_text(encoding='ascii', errors='replace')

    # Split by form feed for pages
    raw_pages = content.split('\x0C')
    pages = []
    all_lines = []

    for page_idx, page_content in enumerate(raw_pages):
        lines = page_content.splitlines()
        pages.append({
            'page_num': page_idx + 1,
            'lines': lines,
        })
        all_lines.extend(lines)

    return {
        'format': 'brf',
        'raw_lines': all_lines,
        'pages': pages,
        'metadata': {
            'filename': path.name,
            'total_lines': len(all_lines),
            'total_pages': len(pages),
        },
    }


def load_unicode_braille(file_path: str) -> dict:
    """
    Load a Unicode braille text file.

    Page breaks are marked by '=== PAGE BREAK ===' lines.

    Returns:
        {
            "format": "unicode",
            "raw_lines": [...],
            "pages": [ {"page_num": 1, "lines": [...]} ],
            "metadata": {"filename": "...", "total_lines": N, "total_pages": N}
        }
    """
    path = Path(file_path)
    content = path.read_text(encoding='utf-8')

    PAGE_BREAK_MARKER = '=== PAGE BREAK ==='

    raw_lines = content.splitlines()
    pages = []
    current_page_lines = []
    page_num = 1

    for line in raw_lines:
        if line.strip() == PAGE_BREAK_MARKER:
            pages.append({
                'page_num': page_num,
                'lines': current_page_lines,
            })
            current_page_lines = []
            page_num += 1
        else:
            current_page_lines.append(line)

    # Last page
    if current_page_lines:
        pages.append({
            'page_num': page_num,
            'lines': current_page_lines,
        })

    # raw_lines without page break markers
    clean_lines = [l for l in raw_lines if l.strip() != PAGE_BREAK_MARKER]

    return {
        'format': 'unicode',
        'raw_lines': clean_lines,
        'pages': pages,
        'metadata': {
            'filename': path.name,
            'total_lines': len(clean_lines),
            'total_pages': len(pages),
        },
    }


def load_braille(file_path: str) -> dict:
    """
    Auto-detect format and load braille file.
    Uses file extension: .brf -> BRF, otherwise -> Unicode.
    """
    path = Path(file_path)
    if path.suffix.lower() == '.brf':
        return load_brf(file_path)
    return load_unicode_braille(file_path)

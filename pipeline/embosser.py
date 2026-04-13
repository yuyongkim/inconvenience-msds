"""
Braille output formats for embossers and visual display.

Generates:
  - BRF (Braille Ready Format): ASCII-encoded braille for embossers
  - Unicode text: UTF-8 braille characters for screen/download
  - PDF: Visual braille dot representation for sighted readers

BRF is the standard embosser input format (40 cells × 25 lines per page).
"""

from __future__ import annotations
import textwrap
from pathlib import Path

# Unicode braille → BRF ASCII mapping
# BRF uses a specific ASCII encoding where each printable character maps to a braille cell
UNICODE_TO_BRF = {}

# Build mapping from dots to BRF ASCII
# BRF ASCII: space=0x20, a-z map to dots, digits map to dots, etc.
_BRF_TABLE = (
    # Dot pattern → BRF ASCII character
    # Ordered by Unicode braille offset (0x2800 + offset)
    ' A1B\'K2L@CIF/MSP"E3H9O6R^DJG>NTQ,'
    '*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)='
)

for i, ch in enumerate(_BRF_TABLE):
    UNICODE_TO_BRF[chr(0x2800 + i)] = ch


def unicode_to_brf(braille_text: str, cells_per_line: int = 40,
                    lines_per_page: int = 25) -> str:
    """
    Convert Unicode braille text to BRF format.

    BRF standard: 40 cells per line, 25 lines per page, form feed between pages.

    Args:
        braille_text: Unicode braille string (U+2800-U+28FF)
        cells_per_line: Cells per line (standard: 40)
        lines_per_page: Lines per page (standard: 25)

    Returns:
        BRF-encoded ASCII string
    """
    lines = braille_text.split('\n')
    brf_lines = []

    for line in lines:
        # Convert each Unicode braille character to BRF ASCII
        brf_chars = []
        for ch in line:
            if ch in UNICODE_TO_BRF:
                brf_chars.append(UNICODE_TO_BRF[ch])
            elif ch == ' ':
                brf_chars.append(' ')
            else:
                brf_chars.append(' ')  # Unknown → space

        brf_line = ''.join(brf_chars)

        # Wrap long lines
        if len(brf_line) > cells_per_line:
            wrapped = textwrap.wrap(brf_line, width=cells_per_line,
                                   break_on_hyphens=False)
            brf_lines.extend(wrapped)
        else:
            brf_lines.append(brf_line)

    # Insert form feeds between pages
    if lines_per_page > 0:
        pages = []
        for i in range(0, len(brf_lines), lines_per_page):
            page = brf_lines[i:i + lines_per_page]
            pages.append('\r\n'.join(page))
        return '\f'.join(pages) + '\r\n'
    else:
        return '\r\n'.join(brf_lines) + '\r\n'


def save_brf(braille_text: str, output_path: str, **kwargs) -> str:
    """Save braille text as BRF file for embossers."""
    brf = unicode_to_brf(braille_text, **kwargs)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='ascii', errors='replace') as f:
        f.write(brf)
    return output_path


def save_unicode_braille(braille_text: str, output_path: str) -> str:
    """Save braille text as UTF-8 Unicode braille file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(braille_text)
    return output_path


# ---------------------------------------------------------------------------
# PDF generation (visual braille dots)
# ---------------------------------------------------------------------------

def _dots_from_unicode(ch: str) -> list[int]:
    """Extract active dot numbers (1-8) from a Unicode braille character."""
    offset = ord(ch) - 0x2800
    if offset < 0 or offset > 0xFF:
        return []
    dots = []
    for bit in range(8):
        if offset & (1 << bit):
            dots.append(bit + 1)
    return dots


def generate_braille_pdf(braille_text: str, output_path: str,
                         title: str = "Braille Document",
                         cells_per_line: int = 32,
                         lines_per_page: int = 25) -> str:
    """
    Generate a PDF with visual braille dot representation.

    Each braille cell is rendered as a 2×4 grid of dots (filled/empty).
    This is for sighted readers to visually inspect braille output.

    Args:
        braille_text: Unicode braille string
        output_path: PDF output path
        title: Document title
        cells_per_line: Braille cells per line
        lines_per_page: Lines per page

    Returns:
        Output file path
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
    except ImportError:
        raise ImportError("reportlab required for PDF generation. Install: pip install reportlab")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    page_w, page_h = A4
    margin_x = 15 * mm
    margin_top = 20 * mm
    margin_bottom = 15 * mm

    # Braille cell dimensions
    dot_radius = 0.8 * mm
    dot_spacing_h = 2.5 * mm   # horizontal between dots in cell
    dot_spacing_v = 2.5 * mm   # vertical between dots in cell
    cell_width = 6.0 * mm      # total cell width
    cell_height = 10.0 * mm    # total cell height (4 rows)
    line_spacing = 3.0 * mm    # extra space between lines

    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle(title)

    # Split into lines and wrap
    raw_lines = braille_text.split('\n')
    all_lines = []
    for line in raw_lines:
        if len(line) > cells_per_line:
            for i in range(0, len(line), cells_per_line):
                all_lines.append(line[i:i + cells_per_line])
        else:
            all_lines.append(line)

    # Title on first page
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, page_h - margin_top + 5 * mm, title)
    c.setFont("Helvetica", 9)
    c.drawString(margin_x, page_h - margin_top - 2 * mm,
                 f"({len(all_lines)} lines, {sum(len(l) for l in all_lines)} cells)")

    y_start = page_h - margin_top - 12 * mm
    y = y_start
    line_idx = 0

    # Dot positions within a cell (relative to cell top-left)
    # Standard 6-dot: dots 1,2,3 (left column), 4,5,6 (right column)
    DOT_POS = {
        1: (0, 0),
        2: (0, 1),
        3: (0, 2),
        4: (1, 0),
        5: (1, 1),
        6: (1, 2),
        7: (0, 3),  # 8-dot extension
        8: (1, 3),
    }

    for line in all_lines:
        if y - cell_height < margin_bottom:
            c.showPage()
            y = page_h - margin_top
            line_idx = 0

        x = margin_x
        for ch in line:
            if 0x2800 <= ord(ch) <= 0x28FF:
                active_dots = _dots_from_unicode(ch)
                # Draw all 6 dot positions
                for dot_num in range(1, 7):
                    col, row = DOT_POS[dot_num]
                    dx = x + col * dot_spacing_h + dot_radius
                    dy = y - row * dot_spacing_v - dot_radius

                    if dot_num in active_dots:
                        c.setFillColorRGB(0, 0, 0)
                        c.circle(dx, dy, dot_radius, fill=1)
                    else:
                        c.setStrokeColorRGB(0.8, 0.8, 0.8)
                        c.setFillColorRGB(1, 1, 1)
                        c.circle(dx, dy, dot_radius, fill=1, stroke=1)

            x += cell_width

        y -= cell_height + line_spacing
        line_idx += 1

    c.save()
    return output_path


def format_msds_braille(name: str, sections: list[dict]) -> str:
    """
    Format MSDS sections into a single braille document suitable for embossing.

    Args:
        name: Chemical name
        sections: List of {section_no, title, text_ko, braille}

    Returns:
        Concatenated braille text with section headers
    """
    from pipeline.ko_braille import encode_korean_braille

    parts = []
    # Title line
    title_braille = encode_korean_braille(name)
    parts.append(title_braille)
    parts.append('')  # blank line

    for sec in sorted(sections, key=lambda s: s['section_no']):
        # Section header
        header = f"{sec['section_no']}. {sec['title']}"
        header_braille = encode_korean_braille(header)
        parts.append(header_braille)

        # Section content
        if sec.get('braille'):
            parts.append(sec['braille'])
        elif sec.get('text_ko'):
            parts.append(encode_korean_braille(sec['text_ko']))

        parts.append('')  # blank line between sections

    return '\n'.join(parts)


if __name__ == '__main__':
    # Demo
    from pipeline.ko_braille import encode_korean_braille

    sample = "화학물질 안전 정보: 벤젠"
    braille = encode_korean_braille(sample)
    print(f"Text:    {sample}")
    print(f"Braille: {braille}")

    brf = unicode_to_brf(braille)
    print(f"BRF:     {brf.strip()}")

    # Test BRF save
    save_brf(braille, "results/demo_embosser.brf")
    print("BRF saved to results/demo_embosser.brf")

    # Test PDF if reportlab available
    try:
        generate_braille_pdf(braille, "results/demo_braille.pdf", title=sample)
        print("PDF saved to results/demo_braille.pdf")
    except ImportError:
        print("PDF skipped (reportlab not installed)")

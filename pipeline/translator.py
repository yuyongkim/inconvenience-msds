"""
Structure-preserving English → Korean translator.

Translates text block-by-block, preserving document structure (P/L/T/M).
Uses Google Translate (free, no API key) via deep-translator.

Interface:
    translate_document(corrected_text, blocks) -> korean_text, korean_blocks
"""

from __future__ import annotations
import re
import time
from deep_translator import GoogleTranslator


_translator = GoogleTranslator(source='en', target='ko')


def translate_text(text: str) -> str:
    """Translate a single English text to Korean."""
    if not text.strip():
        return text
    try:
        # deep-translator has 5000 char limit per call
        if len(text) > 4500:
            return _translate_long(text)
        result = _translator.translate(text)
        return result if result else text
    except Exception as e:
        print(f"  [WARN] Translation failed: {e}")
        return text


def _translate_long(text: str) -> str:
    """Split long text into chunks and translate each."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ''
    for sent in sentences:
        if len(current) + len(sent) > 4000:
            chunks.append(current)
            current = sent
        else:
            current = (current + ' ' + sent).strip()
    if current:
        chunks.append(current)

    translated = []
    for chunk in chunks:
        try:
            r = _translator.translate(chunk)
            translated.append(r if r else chunk)
            time.sleep(0.3)  # rate limiting
        except Exception:
            translated.append(chunk)
    return ' '.join(translated)


def translate_block(text: str, block_type: str) -> str:
    """
    Translate a single block, respecting its type.

    P: translate as paragraph
    L: translate each list item separately (preserve markers)
    T: translate cell contents (preserve structure)
    M: keep math as-is (don't translate formulas)
    """
    if block_type == 'M':
        # Math blocks: don't translate, preserve as-is
        return text

    if block_type == 'L':
        # List: translate each line separately to preserve structure
        lines = text.split('\n')
        translated_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                translated_lines.append('')
                continue

            # Extract list marker (e.g., "1.", "-", "*")
            marker_match = re.match(r'^(\d+[.)]\s*|[-*+]\s*)', stripped)
            if marker_match:
                marker = marker_match.group(0)
                content = stripped[len(marker):]
                translated_content = translate_text(content)
                translated_lines.append(marker + translated_content)
            else:
                translated_lines.append(translate_text(stripped))
            time.sleep(0.2)
        return '\n'.join(translated_lines)

    if block_type == 'T':
        # Table: translate each cell, preserve delimiters
        lines = text.split('\n')
        translated_lines = []
        for line in lines:
            if '|' in line:
                cells = line.split('|')
                translated_cells = []
                for cell in cells:
                    cell_stripped = cell.strip()
                    if cell_stripped and not re.match(r'^[-=:]+$', cell_stripped):
                        translated_cells.append(' ' + translate_text(cell_stripped) + ' ')
                    else:
                        translated_cells.append(cell)
                translated_lines.append('|'.join(translated_cells))
            else:
                translated_lines.append(translate_text(line) if line.strip() else '')
            time.sleep(0.2)
        return '\n'.join(translated_lines)

    # P (paragraph): translate as a whole
    return translate_text(text)


def translate_document(corrected_text: str, blocks: list[dict]) -> tuple[str, list[dict]]:
    """
    Translate entire document block-by-block.

    Args:
        corrected_text: English text (corrected)
        blocks: Structure blocks from extract_structure()

    Returns:
        (korean_text, korean_blocks)
    """
    lines = corrected_text.split('\n')
    korean_parts = []
    korean_blocks = []

    for block in blocks:
        btype = block['type']
        start = block['start_line'] - 1  # 0-based
        end = block['end_line']          # exclusive
        block_text = '\n'.join(lines[start:end])

        print(f"  Translating block {block['block_id']} ({btype}, lines {block['start_line']}-{block['end_line']})...")
        translated = translate_block(block_text, btype)

        ko_lines = translated.split('\n')
        ko_start = len(korean_parts) + 1
        korean_parts.extend(ko_lines)
        korean_parts.append('')  # blank line between blocks
        ko_end = ko_start + len(ko_lines) - 1

        korean_blocks.append({
            'block_id': block['block_id'],
            'type': btype,
            'start_line': ko_start,
            'end_line': ko_end,
        })

    korean_text = '\n'.join(korean_parts).strip()
    return korean_text, korean_blocks

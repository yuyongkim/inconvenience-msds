"""
Output assembler.

Combines decoded text, structure blocks, and optional Korean summary
into the final Phase 1 output JSON format.
"""

from __future__ import annotations
import json
from pathlib import Path


def assemble_output(
    doc_id: str,
    source_path: str,
    rough: str,
    corrected: str,
    blocks: list[dict],
    korean_text: str | None = None,
    korean_blocks: list[dict] | None = None,
    korean_summary: str | None = None,
) -> dict:
    """
    Assemble the final Phase 1 output.

    Returns:
        {
            "doc_id": "...",
            "source_braille_path": "...",
            "english_text": {"rough": "...", "corrected": "..."},
            "structure": {"blocks": [...]},
            "korean_summary": {"text": "...", "num_sentences": N} | null
        }
    """
    result = {
        'doc_id': doc_id,
        'source_braille_path': source_path,
        'english_text': {
            'rough': rough,
            'corrected': corrected,
        },
        'structure': {
            'blocks': blocks,
        },
    }

    # Korean translation
    if korean_text:
        result['korean_text'] = {
            'text': korean_text,
            'blocks': korean_blocks or [],
        }
    else:
        result['korean_text'] = None

    # Korean summary (optional)
    if korean_summary:
        num_sentences = korean_summary.count('.') + korean_summary.count('。')
        if num_sentences == 0:
            num_sentences = 1
        result['korean_summary'] = {
            'text': korean_summary,
            'num_sentences': num_sentences,
        }
    else:
        result['korean_summary'] = None

    return result


def save_output(output: dict, file_path: str) -> None:
    """Save output dict as JSON file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


def to_markdown(output: dict) -> str:
    """
    Convert output to human-readable Markdown.

    Uses structure blocks to format the corrected text.
    """
    lines = []
    lines.append(f'# Document: {output["doc_id"]}')
    lines.append(f'Source: `{output["source_braille_path"]}`')
    lines.append('')

    # English text
    lines.append('## English Text (Corrected)')
    lines.append('')

    corrected = output['english_text']['corrected']
    blocks = output['structure']['blocks']

    if blocks:
        text_lines = corrected.splitlines()
        for block in blocks:
            btype = block['type']
            start = block['start_line'] - 1
            end = block['end_line']
            block_text = '\n'.join(text_lines[start:end]) if end <= len(text_lines) else ''

            if btype == 'P':
                lines.append(block_text)
                lines.append('')
            elif btype == 'L':
                for tl in block_text.splitlines():
                    lines.append(f'- {tl.strip()}')
                lines.append('')
            elif btype == 'T':
                lines.append('```')
                lines.append(block_text)
                lines.append('```')
                lines.append('')
            elif btype == 'M':
                lines.append(f'$$\n{block_text}\n$$')
                lines.append('')
    else:
        lines.append(corrected)
        lines.append('')

    # Korean summary
    if output.get('korean_summary'):
        lines.append('## 한국어 요약')
        lines.append('')
        lines.append(output['korean_summary']['text'])
        lines.append('')

    return '\n'.join(lines)

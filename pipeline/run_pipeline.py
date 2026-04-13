"""
Phase 1 Pipeline – Main entry point.

Usage:
    python -m pipeline.run_pipeline --input data/braille/en/sample_001.brf --output results/sample_001.json
    python -m pipeline.run_pipeline --input data/braille/en/sample_002.txt --output results/sample_002.json --markdown
"""

import argparse
import json
import sys
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.loader import load_braille
from pipeline.decoder import braille_to_text
from pipeline.corrector import correct_noisy_text
from pipeline.structure import extract_structure
from pipeline.assembler import assemble_output, save_output, to_markdown


def run(input_path: str, output_path: str | None = None,
        markdown: bool = False, doc_id: str | None = None,
        translate: bool = False) -> dict:
    """
    Run the full pipeline.

    1. Load braille file
    2. Decode to rough English text
    3. Correct noise
    4. Extract structure
    5. Assemble output

    Returns the output dict.
    """
    path = Path(input_path)
    if doc_id is None:
        doc_id = path.stem

    print(f"[1/5] Loading {path.name}...")
    doc = load_braille(input_path)
    print(f"       Format: {doc['format']}, Lines: {doc['metadata']['total_lines']}, "
          f"Pages: {doc['metadata']['total_pages']}")

    # Join all lines into single braille string
    braille_content = '\n'.join(doc['raw_lines'])

    print(f"[2/5] Decoding braille -> English text...")
    rough_text = braille_to_text(braille_content)
    print(f"       Rough text length: {len(rough_text)} chars")

    print(f"[3/5] Correcting noisy text...")
    corrected_text = correct_noisy_text(rough_text)
    print(f"       Corrected text length: {len(corrected_text)} chars")

    print(f"[4/5] Extracting document structure...")
    # Use decoded text lines for structure detection (more reliable patterns)
    decoded_lines = corrected_text.splitlines()
    blocks = extract_structure(decoded_lines)
    block_types = {}
    for b in blocks:
        block_types[b['type']] = block_types.get(b['type'], 0) + 1
    print(f"       Blocks found: {len(blocks)} ({block_types})")

    # Step 5: Translate (optional)
    korean_text = None
    korean_blocks = None
    total_steps = 6 if translate else 5
    step = 5

    if translate:
        print(f"[{step}/{total_steps}] Translating EN → KR...")
        from pipeline.translator import translate_document
        korean_text, korean_blocks = translate_document(corrected_text, blocks)
        print(f"       Korean text: {len(korean_text)} chars, {len(korean_blocks)} blocks")
        step += 1

    # Step 6: Korean braille (if translated)
    korean_braille = None
    if korean_text:
        step += 1
        total_steps += 1
        print(f"[{step}/{total_steps}] Encoding Korean braille...")
        from pipeline.ko_braille import encode_korean_braille
        korean_braille = encode_korean_braille(korean_text)
        print(f"       Korean braille: {len(korean_braille)} chars")

    step += 1
    print(f"[{step}/{total_steps}] Assembling output...")
    result = assemble_output(
        doc_id=doc_id,
        source_path=input_path,
        rough=rough_text,
        corrected=corrected_text,
        blocks=blocks,
        korean_text=korean_text,
        korean_blocks=korean_blocks,
    )
    if korean_braille:
        result['korean_braille'] = korean_braille

    if output_path:
        save_output(result, output_path)
        print(f"       Saved to {output_path}")

        if markdown:
            md_path = Path(output_path).with_suffix('.md')
            md_content = to_markdown(result)
            md_path.write_text(md_content, encoding='utf-8')
            print(f"       Markdown saved to {md_path}")

    print(f"\nDone. Pipeline completed for {doc_id}.")
    return result


def main():
    parser = argparse.ArgumentParser(description='Phase 1 Braille Interpretation Pipeline')
    parser.add_argument('--input', required=True, help='Input braille file path')
    parser.add_argument('--output', default=None, help='Output JSON path')
    parser.add_argument('--markdown', action='store_true', help='Also generate Markdown output')
    parser.add_argument('--doc-id', default=None, help='Document ID (default: filename stem)')
    parser.add_argument('--translate', action='store_true', help='Translate EN → KR')
    args = parser.parse_args()

    result = run(args.input, args.output, args.markdown, args.doc_id, args.translate)

    if not args.output:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

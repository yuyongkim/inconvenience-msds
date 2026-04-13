"""
Generate sample braille files from the English golden set CSV.

Creates thematic braille documents in data/braille/en/ by grouping
golden set sentences by category.

Usage:
    python scripts/generate_braille_samples.py
"""

import csv
import sys
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.encoder import encode_text_to_braille


def main():
    csv_path = PROJECT_ROOT / 'data' / 'golden_braille_roundtrip_en.csv'
    output_dir = PROJECT_ROOT / 'data' / 'braille' / 'en'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read golden set
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Group by category
    by_cat = defaultdict(list)
    for row in rows:
        by_cat[row['category']].append(row['source_text'])

    # Create one braille file per category
    for cat, sentences in sorted(by_cat.items()):
        # Build document text
        title = f"Sample Document: {cat.upper()}"
        lines = [title, ""]
        for i, sent in enumerate(sentences, 1):
            lines.append(f"{sent}")
            if i < len(sentences):
                lines.append("")  # blank line between sentences

        text = '\n'.join(lines)
        braille = encode_text_to_braille(text)

        out_path = output_dir / f'sample_{cat}.txt'
        out_path.write_text(braille, encoding='utf-8')
        print(f"  {cat}: {len(sentences)} sentences -> {out_path.name}")

    # Also create one combined "mixed" document with page breaks
    all_lines = ["Combined Sample Document", ""]
    for cat, sentences in sorted(by_cat.items()):
        all_lines.append(f"Section: {cat.upper()}")
        all_lines.append("")
        for sent in sentences:
            all_lines.append(sent)
            all_lines.append("")
        all_lines.append("=== PAGE BREAK ===")

    # Remove trailing page break
    if all_lines and all_lines[-1] == "=== PAGE BREAK ===":
        all_lines.pop()

    combined_text = '\n'.join(all_lines)
    # Encode, but preserve page break markers
    parts = combined_text.split('=== PAGE BREAK ===')
    braille_parts = [encode_text_to_braille(p) for p in parts]
    combined_braille = '\n=== PAGE BREAK ===\n'.join(braille_parts)

    out_path = output_dir / 'sample_combined.txt'
    out_path.write_text(combined_braille, encoding='utf-8')
    print(f"  combined: all categories -> {out_path.name}")

    print(f"\nDone. Generated {len(by_cat) + 1} braille files in {output_dir}")


if __name__ == '__main__':
    main()

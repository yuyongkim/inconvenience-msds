"""
Run Phase 1 pipeline on all sample braille files and report results.

Usage:
    python scripts/run_all_samples.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.run_pipeline import run


def main():
    sample_dir = PROJECT_ROOT / 'data' / 'braille' / 'en'
    output_dir = PROJECT_ROOT / 'results' / 'pipeline_outputs'
    output_dir.mkdir(parents=True, exist_ok=True)

    sample_files = sorted(sample_dir.glob('sample_*.txt'))
    print(f"Found {len(sample_files)} sample files\n")

    for f in sample_files:
        doc_id = f.stem
        out_json = output_dir / f'{doc_id}.json'
        print(f"\n{'='*60}")
        result = run(
            input_path=str(f),
            output_path=str(out_json),
            markdown=True,
            doc_id=doc_id,
        )

        # Quick quality check: count blocks by type
        blocks = result['structure']['blocks']
        types = {}
        for b in blocks:
            types[b['type']] = types.get(b['type'], 0) + 1

        corrected = result['english_text']['corrected']
        lines = [l for l in corrected.splitlines() if l.strip()]
        print(f"  -> {len(lines)} non-empty lines, blocks: {types}")

    print(f"\n{'='*60}")
    print(f"All outputs saved to {output_dir}/")


if __name__ == '__main__':
    main()

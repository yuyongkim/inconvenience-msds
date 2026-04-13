"""
Noise injection script for generating noisy English sentences.

Supports 7 noise types defined in the evaluation spec:
  missing_punctuation, merged_words, split_words, spelling_variation,
  dropped_function_words, number_format_noise, mixed_noise

Usage:
    python scripts/inject_noise.py --input data/golden_braille_roundtrip_en.csv \
                                   --output data/noise_correction_eval_en_auto.csv \
                                   --noise-types all \
                                   --seed 42
"""

import argparse
import csv
import random
import re
import string
from pathlib import Path


# ---------------------------------------------------------------------------
# Individual noise functions
# ---------------------------------------------------------------------------

def noise_missing_punctuation(text: str, rng: random.Random) -> str:
    """Remove some or all punctuation marks."""
    targets = ['.', ',', '?', '!', ';', ':', '"', "'", '(', ')']
    result = list(text)
    for i, ch in enumerate(result):
        if ch in targets and rng.random() < 0.6:
            result[i] = ''
    out = ''.join(result).strip()
    return out if out else text


def noise_merged_words(text: str, rng: random.Random) -> str:
    """Remove spaces between randomly selected adjacent word pairs."""
    words = text.split()
    if len(words) < 3:
        return text
    n_merges = max(1, len(words) // 5)
    indices = list(range(len(words) - 1))
    rng.shuffle(indices)
    merge_at = set(indices[:n_merges])
    result = []
    i = 0
    while i < len(words):
        if i in merge_at and i + 1 < len(words):
            result.append(words[i] + words[i + 1])
            i += 2
        else:
            result.append(words[i])
            i += 1
    return ' '.join(result)


def noise_split_words(text: str, rng: random.Random) -> str:
    """Insert a space inside randomly selected words."""
    words = text.split()
    for idx in range(len(words)):
        w = words[idx]
        if len(w) > 4 and rng.random() < 0.35:
            pos = rng.randint(2, len(w) - 2)
            words[idx] = w[:pos] + ' ' + w[pos:]
    return ' '.join(words)


def noise_spelling_variation(text: str, rng: random.Random) -> str:
    """Introduce character-level spelling errors."""
    words = text.split()
    for idx in range(len(words)):
        w = words[idx]
        if len(w) > 3 and rng.random() < 0.3:
            pos = rng.randint(1, len(w) - 2)
            action = rng.choice(['swap', 'delete', 'replace'])
            chars = list(w)
            if action == 'swap' and pos + 1 < len(chars):
                chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
            elif action == 'delete':
                chars.pop(pos)
            elif action == 'replace':
                chars[pos] = rng.choice(string.ascii_lowercase)
            words[idx] = ''.join(chars)
    return ' '.join(words)


FUNCTION_WORDS = {
    'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been',
    'of', 'to', 'in', 'on', 'at', 'for', 'by', 'with', 'from',
    'that', 'this', 'it', 'its', 'has', 'have', 'had', 'do', 'does',
}


def noise_dropped_function_words(text: str, rng: random.Random) -> str:
    """Drop function words (articles, prepositions, auxiliaries)."""
    words = text.split()
    result = [w for w in words if not (w.lower() in FUNCTION_WORDS and rng.random() < 0.55)]
    return ' '.join(result) if result else text


def noise_number_format(text: str, rng: random.Random) -> str:
    """Corrupt number formatting: remove commas, decimal points, unit symbols."""
    # Remove commas inside numbers (e.g., 1,234 -> 1234)
    out = re.sub(r'(\d),(\d)', r'\1\2', text)
    # Randomly remove decimal points
    if rng.random() < 0.4:
        out = re.sub(r'(\d)\.(\d)', r'\1\2', out)
    # Remove common unit symbols
    for sym in ['%', '$', '°C', '°', 'kg', 'mg', 'MPa', 'mm', 'ms']:
        if sym in out and rng.random() < 0.4:
            out = out.replace(sym, '')
    return out.strip()


def noise_mixed(text: str, rng: random.Random) -> str:
    """Apply 2-3 noise types together."""
    fns = [
        noise_missing_punctuation,
        noise_merged_words,
        noise_split_words,
        noise_spelling_variation,
        noise_dropped_function_words,
        noise_number_format,
    ]
    k = rng.randint(2, 3)
    chosen = rng.sample(fns, k)
    result = text
    for fn in chosen:
        result = fn(result, rng)
    return result


NOISE_FN_MAP = {
    'missing_punctuation': noise_missing_punctuation,
    'merged_words': noise_merged_words,
    'split_words': noise_split_words,
    'spelling_variation': noise_spelling_variation,
    'dropped_function_words': noise_dropped_function_words,
    'number_format_noise': noise_number_format,
    'mixed_noise': noise_mixed,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Inject noise into clean English sentences')
    parser.add_argument('--input', required=True, help='Input CSV with source_text column')
    parser.add_argument('--output', required=True, help='Output CSV path')
    parser.add_argument('--noise-types', default='all',
                        help='Comma-separated noise types, or "all"')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)

    if args.noise_types == 'all':
        noise_types = list(NOISE_FN_MAP.keys())
    else:
        noise_types = [t.strip() for t in args.noise_types.split(',')]

    # Read input
    rows = []
    with open(args.input, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Generate noisy variants
    output_rows = []
    counter = 1
    for row in rows:
        clean = row['source_text']
        for ntype in noise_types:
            fn = NOISE_FN_MAP[ntype]
            noisy = fn(clean, rng)
            # Skip if noise didn't change anything
            if noisy == clean:
                noisy = fn(clean, rng)
            output_rows.append({
                'id': f'nc_{counter:03d}',
                'clean_en': clean,
                'noisy_en': noisy,
                'noise_type': ntype,
                'corrected_en': '',
            })
            counter += 1

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'clean_en', 'noisy_en', 'noise_type', 'corrected_en'])
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Generated {len(output_rows)} noisy samples -> {output_path}")
    for nt in noise_types:
        count = sum(1 for r in output_rows if r['noise_type'] == nt)
        print(f"  {nt}: {count}")


if __name__ == '__main__':
    main()

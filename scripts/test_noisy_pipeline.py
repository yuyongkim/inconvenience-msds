"""
Simulate realistic braille-to-text pipeline with noise.

Process:
  1. Take original English text
  2. Encode to braille
  3. Inject braille-level noise (cell corruption, deletion)
  4. Decode corrupted braille
  5. Apply corrector
  6. Measure quality at each stage

This simulates what happens with real-world BRF files that have
scanning errors, formatting artifacts, or encoding issues.
"""

import sys
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.encoder import encode_text_to_braille
from pipeline.decoder import braille_to_text
from pipeline.corrector import correct_noisy_text
from eval.similarity import normalized_edit_similarity, chrf_score


def corrupt_braille(braille: str, corruption_rate: float = 0.05,
                    seed: int = 42) -> str:
    """
    Introduce noise at the braille cell level.

    Types of corruption:
      - Cell deletion (remove a braille character)
      - Cell substitution (replace with random braille cell)
      - Space insertion/deletion
    """
    rng = random.Random(seed)
    chars = list(braille)
    result = []

    for ch in chars:
        if ch == '\n':
            result.append(ch)
            continue

        r = rng.random()
        if r < corruption_rate * 0.4:
            # Delete this cell
            continue
        elif r < corruption_rate * 0.8:
            # Substitute with random braille cell
            result.append(chr(0x2800 + rng.randint(0, 63)))
        elif r < corruption_rate:
            # Insert extra space
            result.append('\u2800')
            result.append(ch)
        else:
            result.append(ch)

    return ''.join(result)


TEXTS = {
    'narrative': (
        'Down, down, down. There was nothing else to do, so Alice soon '
        'began talking again. "Dinah will miss me very much tonight, I '
        'should think!" She felt that she was dozing off, and had just '
        'begun to dream that she was walking hand in hand with Dinah.'
    ),
    'technical': (
        'The rate of a chemical reaction depends on the concentration '
        'of reactants, temperature, and the presence of a catalyst. '
        'For every 10 degree increase in temperature, the reaction '
        'rate approximately doubles.'
    ),
    'numeric': (
        'The HTTP status code 404 means the resource was not found. '
        'The yield strength of A36 steel is approximately 250 MPa. '
        'A sample of 30 students had a mean score of 75 points.'
    ),
    'structured': (
        'Computer Networking\n\n'
        'Networks are classified by scope:\n'
        '1. LAN: covers a building.\n'
        '2. MAN: spans a city.\n'
        '3. WAN: connects countries.\n\n'
        'The TCP/IP stack has 4 layers.'
    ),
}


def run_test(name: str, text: str, corruption_rates: list[float]):
    print(f"\n--- {name} ({len(text)} chars) ---")
    braille = encode_text_to_braille(text)

    for rate in corruption_rates:
        corrupted = corrupt_braille(braille, corruption_rate=rate)
        decoded = braille_to_text(corrupted)
        corrected = correct_noisy_text(decoded)

        sim_decoded = normalized_edit_similarity(text, decoded)
        sim_corrected = normalized_edit_similarity(text, corrected)
        delta = sim_corrected - sim_decoded

        chrf_decoded = chrf_score(text, decoded)
        chrf_corrected = chrf_score(text, corrected)

        print(f"  noise={rate:.0%}:  decoded={sim_decoded:.3f}  "
              f"corrected={sim_corrected:.3f}  delta={delta:+.3f}  "
              f"chrF={chrf_decoded:.3f}->{chrf_corrected:.3f}")


def main():
    rates = [0.0, 0.02, 0.05, 0.10, 0.15, 0.20]

    for name, text in TEXTS.items():
        run_test(name, text, rates)

    # Summary: average across all texts at each rate
    print(f"\n{'='*60}")
    print("  AVERAGE ACROSS ALL SAMPLES")
    print(f"{'='*60}")
    print(f"  {'Rate':>6}  {'Decoded':>10}  {'Corrected':>10}  {'Delta':>10}")
    print(f"  {'-'*42}")

    for rate in rates:
        sims_dec, sims_cor = [], []
        for text in TEXTS.values():
            braille = encode_text_to_braille(text)
            corrupted = corrupt_braille(braille, corruption_rate=rate)
            decoded = braille_to_text(corrupted)
            corrected = correct_noisy_text(decoded)
            sims_dec.append(normalized_edit_similarity(text, decoded))
            sims_cor.append(normalized_edit_similarity(text, corrected))

        avg_dec = sum(sims_dec) / len(sims_dec)
        avg_cor = sum(sims_cor) / len(sims_cor)
        print(f"  {rate:>5.0%}  {avg_dec:>10.4f}  {avg_cor:>10.4f}  {avg_cor - avg_dec:>+10.4f}")


if __name__ == '__main__':
    main()

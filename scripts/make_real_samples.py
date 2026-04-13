"""
Create realistic braille sample files from public domain English texts.

Downloads/uses excerpts from:
  1. Alice in Wonderland (narrative)
  2. A chemistry textbook-style passage (manually crafted, domain-specific)
  3. A CS/networking passage (manually crafted, technical)

Encodes each to Unicode braille and saves as sample files.
Then runs the full pipeline on each and reports decode quality.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.encoder import encode_text_to_braille, encode_document
from pipeline.decoder import braille_to_text
from pipeline.corrector import correct_noisy_text
from pipeline.structure import extract_structure
from pipeline.assembler import assemble_output, save_output, to_markdown
from eval.similarity import normalized_edit_similarity, chrf_score

OUTPUT_DIR = PROJECT_ROOT / 'data' / 'braille' / 'en' / 'real'
RESULT_DIR = PROJECT_ROOT / 'results' / 'real_samples'


# ---------------------------------------------------------------------------
# Sample texts (public domain / self-authored)
# ---------------------------------------------------------------------------

SAMPLES = {
    'alice': {
        'title': 'Alice in Wonderland (Excerpt)',
        'text': """\
Down, down, down. There was nothing else to do, so Alice soon began talking again. "Dinah'll miss me very much to-night, I should think!" (Dinah was the cat.) "I hope they'll remember her saucer of milk at tea-time. Dinah my dear! I wish you were down here with me! There are no mice in the air, I'm afraid, but you might catch a bat, and that's very like a mouse, you know. But do cats eat bats, I wonder?"

And here Alice began to get rather sleepy, and went on saying to herself, in a dreamy sort of way, "Do cats eat bats? Do cats eat bats?" and sometimes, "Do bats eat cats?" for, you see, as she couldn't answer either question, it didn't much matter which way she put it.

She felt that she was dozing off, and had just begun to dream that she was walking hand in hand with Dinah, and saying to her very earnestly, "Now, Dinah, tell me the truth: did you ever eat a bat?" when suddenly, thump! thump! down she came upon a heap of sticks and dry leaves, and the fall was over.""",
    },

    'chemistry': {
        'title': 'Introduction to Chemical Kinetics',
        'text': """\
Chemical Kinetics

The rate of a chemical reaction depends on several factors: the concentration of reactants, temperature, and the presence of a catalyst.

1. Effect of Concentration
The higher the concentration of reactants, the greater the frequency of molecular collisions, leading to a faster reaction rate.

2. Effect of Temperature
For every 10 degree increase in temperature, the reaction rate approximately doubles. This relationship is described by the Arrhenius equation: k = A * exp(-Ea/RT), where k is the rate constant, A is the pre-exponential factor, Ea is the activation energy, R is the gas constant (8.314 J/mol*K), and T is the absolute temperature in Kelvin.

3. Role of Catalysts
A catalyst lowers the activation energy of a reaction without being consumed. For example, platinum is used as a catalyst in the catalytic converter of automobiles, where it helps convert harmful CO and NO gases into CO2 and N2.""",
    },

    'networking': {
        'title': 'Computer Networking Basics',
        'text': """\
Computer Networking

A computer network is a system of interconnected devices that can exchange data. Networks are classified by their geographic scope:

- LAN (Local Area Network): covers a building or campus.
- MAN (Metropolitan Area Network): spans a city.
- WAN (Wide Area Network): connects cities, countries, or continents.

The TCP/IP protocol stack is the foundation of Internet communication. Data is transmitted in packets, each containing a source address and destination address. The 4 layers are:

1. Application Layer (HTTP, FTP, DNS)
2. Transport Layer (TCP, UDP)
3. Internet Layer (IP, ICMP)
4. Link Layer (Ethernet, Wi-Fi)

The HTTP status code 404 indicates that the requested resource was not found on the server. Status code 200 means the request was successful. Status code 500 indicates an internal server error.""",
    },

    'statistics': {
        'title': 'Introduction to Statistics',
        'text': """\
Statistics is the science of collecting, analyzing, and interpreting data.

Descriptive Statistics:
The mean, median, and mode are measures of central tendency. The standard deviation and variance measure the spread of data. For a sample of n values, the mean is calculated as: sum of all values divided by n.

Inferential Statistics:
We use sample data to make inferences about a population. In hypothesis testing, if the p-value is less than 0.05, we reject the null hypothesis.

Example: A sample of 30 students had a mean test score of 75 with a standard deviation of 10. The 95% confidence interval is approximately 71.4 to 78.6.

Correlation measures the strength and direction of the linear relationship between two variables. The correlation coefficient r ranges from -1 to 1, where r = 1 indicates a perfect positive correlation and r = -1 indicates a perfect negative correlation.""",
    },
}


def process_sample(name: str, info: dict):
    """Encode text to braille, decode back, measure quality."""
    print(f"\n{'='*60}")
    print(f"  {info['title']}")
    print(f"{'='*60}")

    text = info['text']

    # Encode to braille
    braille = encode_document(text, lines_per_page=0)

    # Save braille file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    braille_path = OUTPUT_DIR / f'{name}.txt'
    braille_path.write_text(braille, encoding='utf-8')
    print(f"  Braille file: {braille_path.name} ({len(braille)} chars)")

    # Decode back
    decoded = braille_to_text(braille)
    corrected = correct_noisy_text(decoded)

    # Measure quality
    sim_raw = normalized_edit_similarity(text, decoded)
    sim_corrected = normalized_edit_similarity(text, corrected)
    chrf_raw = chrf_score(text, decoded)
    chrf_corrected = chrf_score(text, corrected)

    print(f"  Raw decode:   edit_sim={sim_raw:.4f}  chrF={chrf_raw:.4f}")
    print(f"  After correct: edit_sim={sim_corrected:.4f}  chrF={chrf_corrected:.4f}")
    print(f"  Delta:         edit_sim={sim_corrected - sim_raw:+.4f}  chrF={chrf_corrected - chrf_raw:+.4f}")

    # Extract structure
    blocks = extract_structure(corrected.splitlines())
    block_types = {}
    for b in blocks:
        block_types[b['type']] = block_types.get(b['type'], 0) + 1
    print(f"  Structure:     {len(blocks)} blocks {block_types}")

    # Assemble and save output
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    result = assemble_output(
        doc_id=name,
        source_path=str(braille_path),
        rough=decoded,
        corrected=corrected,
        blocks=blocks,
    )
    save_output(result, str(RESULT_DIR / f'{name}.json'))

    md_path = RESULT_DIR / f'{name}.md'
    md_path.write_text(to_markdown(result), encoding='utf-8')

    return {
        'name': name,
        'chars': len(text),
        'sim_raw': sim_raw,
        'sim_corrected': sim_corrected,
        'chrf_raw': chrf_raw,
        'chrf_corrected': chrf_corrected,
        'blocks': block_types,
    }


def main():
    results = []
    for name, info in SAMPLES.items():
        r = process_sample(name, info)
        results.append(r)

    # Summary table
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Sample':<15} {'Chars':>6} {'Raw Edit':>10} {'Corr Edit':>10} {'Raw ChrF':>10} {'Corr ChrF':>10}")
    print(f"  {'-'*65}")
    for r in results:
        print(f"  {r['name']:<15} {r['chars']:>6} {r['sim_raw']:>10.4f} {r['sim_corrected']:>10.4f} "
              f"{r['chrf_raw']:>10.4f} {r['chrf_corrected']:>10.4f}")

    avg_raw = sum(r['sim_raw'] for r in results) / len(results)
    avg_corr = sum(r['sim_corrected'] for r in results) / len(results)
    avg_chrf_raw = sum(r['chrf_raw'] for r in results) / len(results)
    avg_chrf_corr = sum(r['chrf_corrected'] for r in results) / len(results)
    print(f"  {'-'*65}")
    print(f"  {'AVERAGE':<15} {'':>6} {avg_raw:>10.4f} {avg_corr:>10.4f} "
          f"{avg_chrf_raw:>10.4f} {avg_chrf_corr:>10.4f}")


if __name__ == '__main__':
    main()

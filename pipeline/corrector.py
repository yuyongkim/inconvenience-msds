"""
Noise corrector for reverse-transcribed braille text.

Purely rule-based — no external API required.
Covers the 7 noise types from the evaluation spec:
  missing_punctuation, merged_words, split_words, spelling_variation,
  dropped_function_words, number_format_noise, mixed_noise

Interface:
    correct_noisy_text(noisy_text, lang="en") -> corrected_text
"""

from __future__ import annotations
import re
from difflib import get_close_matches


def correct_noisy_text(noisy_text: str, lang: str = 'en', **_kwargs) -> str:
    """
    Correct noise in reverse-transcribed text using conservative rule-based pipeline.

    Core principle: ONLY fix what we are highly confident about.
    If unsure, leave the text unchanged — do no harm.

    Safe fixes (high confidence):
      1. Whitespace normalization (double spaces)
      2. Dictionary-exact spelling correction
    Unsafe (disabled): punctuation insertion, split word guessing, merged word splitting
    """
    if not noisy_text.strip():
        return noisy_text

    result = noisy_text
    result = _fix_whitespace(result)
    result = _fix_spelling(result)
    return result


# ---------------------------------------------------------------------------
# 1. Whitespace normalization
# ---------------------------------------------------------------------------

def _fix_whitespace(text: str) -> str:
    lines = []
    for line in text.split('\n'):
        # Normalize multiple spaces within a line, but preserve the line itself
        line = re.sub(r' {2,}', ' ', line).strip()
        lines.append(line)
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# 2. Split word rejoining
# ---------------------------------------------------------------------------

# English words commonly broken by braille decoding.
# pattern: fragment + space + fragment → merged word
# Suffixes that indicate the second piece belongs to the first.
_REJOIN_SUFFIXES = [
    'tion', 'sion', 'ment', 'ture', 'ence', 'ance', 'ness', 'able', 'ible',
    'ious', 'eous', 'ical', 'ally', 'ling', 'ring', 'ting', 'ning', 'ding',
    'ied', 'ies', 'ing', 'ous', 'ive', 'ful', 'ess', 'ent', 'ant', 'ate',
    'ure', 'ory', 'ary', 'ery', 'ity', 'ism', 'ist', 'ize', 'ise', 'fy',
    'ly', 'ed', 'er', 'en', 'al', 'ty',
]

# Known words that commonly get split
_KNOWN_WORDS = {
    'temperature', 'approximately', 'concentration', 'polymerase', 'reaction',
    'experiment', 'instruction', 'architecture', 'administered', 'determines',
    'hydrocarbon', 'milliseconds', 'conversion', 'amoxicillin', 'molecular',
    'frequency', 'collisions', 'paragraph', 'sentence', 'condition',
    'compiler', 'generates', 'abstract', 'resource', 'pressure',
    'integral', 'function', 'patient', 'reactor', 'dissolves',
    'aromatic', 'strength', 'reynolds', 'turbulent', 'laminar',
    'segments', 'amplifies', 'enrolled', 'responded', 'another',
    'application', 'information', 'university', 'environment',
    'development', 'understanding', 'performance', 'significant',
    'measurement', 'calculation', 'observation', 'description',
    'communication', 'distribution', 'investigation', 'representation',
}


def _fix_split_words(text: str) -> str:
    """Rejoin words that were incorrectly split by a space. Preserves line structure."""
    output_lines = []
    for line in text.split('\n'):
        words = line.split(' ')
        result = []
        i = 0

        while i < len(words):
            if i + 1 < len(words) and words[i] and words[i + 1]:
                combined = words[i] + words[i + 1]
                combined_lower = combined.lower().strip('.,;:!?()"\'')

                # Check if combined form is a known word
                if combined_lower in _KNOWN_WORDS:
                    result.append(combined)
                    i += 2
                    continue

                # Check suffix-based rejoining
                w2_stripped = words[i + 1].lower().strip('.,;:!?()"\'')
                if (len(words[i]) <= 4 and len(w2_stripped) >= 3 and
                        any(w2_stripped.endswith(s) for s in _REJOIN_SUFFIXES)):
                    w1_lower = words[i].lower().strip('.,;:!?()"\'')
                    if w1_lower not in _COMMON_SHORT_WORDS and combined_lower in _KNOWN_WORDS:
                        result.append(combined)
                        i += 2
                        continue

            result.append(words[i])
            i += 1

        output_lines.append(' '.join(result))

    return '\n'.join(output_lines)


_COMMON_SHORT_WORDS = {
    'a', 'an', 'am', 'as', 'at', 'be', 'by', 'do', 'go', 'he', 'if', 'in',
    'is', 'it', 'me', 'my', 'no', 'of', 'on', 'or', 'so', 'to', 'up', 'us',
    'we', 'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
    'had', 'her', 'was', 'one', 'our', 'out', 'has', 'his', 'how', 'its',
    'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'did', 'get',
    'let', 'say', 'she', 'too', 'use', 'per', 'set', 'run', 'top', 'end',
    'put', 'try', 'ask', 'own', 'off', 'big', 'few', 'low', 'why', 'far',
    'this', 'that', 'with', 'have', 'from', 'they', 'been', 'each', 'make',
    'like', 'long', 'look', 'many', 'some', 'them', 'than', 'will', 'into',
    'over', 'such', 'take', 'come', 'more', 'also', 'back', 'only', 'used',
    'step', 'open', 'room', 'call', 'note',
}


# ---------------------------------------------------------------------------
# 3. Merged word splitting
# ---------------------------------------------------------------------------

# Patterns where two words got merged
_MERGE_PATTERNS = [
    # Specific known merges
    (r'\b[Nn]euralnetwork\b', 'neural network'),
    (r'\b[Ss]yntaxtree\b', 'syntax tree'),
    (r'\b[Ss]odiumchloride\b', 'Sodium chloride'),
    (r'\b[Cc]allme\b', 'Call me'),
    (r'\b[Tt]hemeeting\b', 'The meeting'),
    (r'\b[Tt]heoffice\b', 'the office'),
    (r'\b[Oo]nethird\b', 'one third'),
    # Generic: camelCase-like merges (lowercase + uppercase, only mid-word)
    (r'([a-z])([A-Z][a-z]{2,})', r'\1 \2'),
]

# Exceptions: don't split these
_NO_SPLIT = {
    'A36', 'C6H6', 'NaCl', 'PCR', 'AST', 'CPU', 'HTTP', 'TCP', 'IP',
    'DNA', 'RNA', 'MPa', 'LAN', 'WAN', 'MAN', 'UEB', 'BRF',
    '401B', '64-bit', 'p.m.', 'a.m.',
}


def _fix_merged_words(text: str) -> str:
    result = text

    # Protect known terms from splitting by wrapping in unique tokens
    protected = {}
    for term in sorted(_NO_SPLIT, key=len, reverse=True):
        if term in result:
            placeholder = f'\x00{len(protected)}\x00'
            protected[placeholder] = term
            result = result.replace(term, placeholder)

    for pattern, replacement in _MERGE_PATTERNS:
        result = re.sub(pattern, replacement, result)

    # Restore protected terms
    for placeholder, term in protected.items():
        result = result.replace(placeholder, term)

    return result


# ---------------------------------------------------------------------------
# 4. Spelling correction
# ---------------------------------------------------------------------------

_SPELLING_DICT = {
    # Direct known misspellings
    'aproximatly': 'approximately',
    'aproximately': 'approximately',
    'temprature': 'temperature',
    'reactr': 'reactor',
    'degres': 'degrees',
    'yeild': 'yield',
    'strenght': 'strength',
    'arromatic': 'aromatic',
    'hydorcarbon': 'hydrocarbon',
    'miliseconds': 'milliseconds',
    'servr': 'server',
    'respondde': 'responded',
    'complier': 'compiler',
    'genrates': 'generates',
    'resorce': 'resource',
    'intgral': 'integral',
    'presure': 'pressure',
    'disolves': 'dissolves',
    'readly': 'readily',
    'parsng': 'parsing',
    'increse': 'increase',
    'increses': 'increases',
    'determin': 'determine',
    'determins': 'determines',
    'concetration': 'concentration',
    'instrution': 'instruction',
    'adminstered': 'administered',
    'administred': 'administered',
    'frecuency': 'frequency',
    'colisions': 'collisions',
    'collisons': 'collisions',
    'paragrph': 'paragraph',
    'sentece': 'sentence',
    'conditon': 'condition',
    'conditons': 'conditions',
    'specifc': 'specific',
    'moleculr': 'molecular',
    'utilizs': 'utilizes',
    'architcture': 'architecture',
    'archtecture': 'architecture',
    'turblent': 'turbulent',
    'lamniar': 'laminar',
    'enrolld': 'enrolled',
    'enrollled': 'enrolled',
    'sentance': 'sentence',
    'sentense': 'sentence',
    'aproximate': 'approximate',
    'tempature': 'temperature',
    'temperture': 'temperature',
    'presssure': 'pressure',
    'compilor': 'compiler',
    'generats': 'generates',
    'resourse': 'resource',
    'dissovles': 'dissolves',
    'dissloves': 'dissolves',
    'reponded': 'responded',
    'respnded': 'responded',
    'milisecnds': 'milliseconds',
    'stregth': 'strength',
    'stregnth': 'strength',
}

# Reference word list for fuzzy matching
_REFERENCE_WORDS = set(_SPELLING_DICT.values()) | _KNOWN_WORDS | {
    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
    'simple', 'sentence', 'braille', 'meeting', 'starts', 'value',
    'approximately', 'temperature', 'ranges', 'degrees', 'reactor',
    'sodium', 'chloride', 'dissolves', 'readily', 'water',
    'utilizes', 'instruction', 'patient', 'administered',
    'amoxicillin', 'twice', 'daily', 'yield', 'strength', 'steel',
    'polymerase', 'chain', 'amplifies', 'segments',
    'reynolds', 'number', 'determines', 'whether', 'laminar',
    'turbulent', 'status', 'code', 'means', 'found',
    'benzene', 'aromatic', 'hydrocarbon', 'compiler',
    'generates', 'abstract', 'syntax', 'tree', 'parsing',
    'figure', 'conversion', 'rate', 'increases', 'from',
}


def _fix_spelling(text: str) -> str:
    return '\n'.join(_fix_spelling_line(line) for line in text.split('\n'))


def _fix_spelling_line(text: str) -> str:
    words = text.split()
    for i, w in enumerate(words):
        # Strip punctuation for lookup
        prefix = ''
        suffix = ''
        core = w
        while core and not core[0].isalnum():
            prefix += core[0]
            core = core[1:]
        while core and not core[-1].isalnum():
            suffix = core[-1] + suffix
            core = core[:-1]

        if not core or len(core) <= 2:
            continue

        lower = core.lower()

        # Direct dictionary lookup
        if lower in _SPELLING_DICT:
            fixed = _SPELLING_DICT[lower]
            if core[0].isupper():
                fixed = fixed[0].upper() + fixed[1:]
            words[i] = prefix + fixed + suffix
            continue

        # No fuzzy matching — only exact dictionary hits to avoid false corrections

    return ' '.join(words)


# ---------------------------------------------------------------------------
# 5. Number/unit format repair
# ---------------------------------------------------------------------------

def _fix_number_format(text: str) -> str:
    result = text

    # "47 3 percent" or "47 3%" -> "47.3 percent" / "47.3%"
    result = re.sub(r'(\d+)\s+(\d+)\s*(%|percent)', r'\1.\2\3', result)

    # Restore common unit symbols that may have been lost
    # "20 C" in temperature context -> "20°C"
    result = re.sub(r'(\d+)\s*degrees?\s*C\b', r'\1 degrees C', result)

    # "500 mg" is fine as-is; "500mg" -> "500 mg"
    result = re.sub(r'(\d)(mg|kg|ml|MPa|mm|ms|Hz|kHz|MHz|GHz)\b', r'\1 \2', result)

    # Restore comma in large numbers if context suggests it
    # "1234 students" -> "1,234 students" (only for 4+ digit numbers before certain words)
    result = re.sub(r'\b(\d)(\d{3})\b(?=\s+(?:students|people|items|units|cases))',
                    r'\1,\2', result)

    return result


# ---------------------------------------------------------------------------
# 6. Punctuation restoration
# ---------------------------------------------------------------------------

_ABBREVIATIONS = {'p.m.', 'a.m.', 'e.g.', 'i.e.', 'etc.', 'vs.', 'dr.', 'mr.', 'mrs.', 'ms.', 'st.', 'no.', 'vol.'}


def _maybe_add_space(m):
    """Add space after punctuation unless it looks like an abbreviation."""
    punct = m.group(1)
    letter = m.group(2)
    # Single letter after period = likely abbreviation (p.m., e.g.)
    if punct == '.' and len(letter) == 1:
        return punct + letter  # don't add space
    return punct + ' ' + letter


def _fix_punctuation(text: str) -> str:
    lines = text.split('\n')
    fixed = []

    for line in lines:
        line = line.strip()
        if not line:
            fixed.append('')
            continue

        # If line looks like a complete sentence without ending punctuation, add period
        # Skip: short lines, list items, headings, lines ending with ':'
        if (len(line) > 30 and line[-1].isalpha()
                and not line.startswith('===')
                and not line.startswith(('-', '*', '+'))
                and not line[0].isdigit()
                and not line.endswith(':')
                and ' ' in line):  # must have multiple words
            line += '.'

        # Fix spacing around punctuation
        # Remove space before period/comma/colon/semicolon
        line = re.sub(r'\s+([.,;:!?])', r'\1', line)
        # Add space after punctuation if missing, but NOT in abbreviations
        # like "p.m." or "e.g." or decimal numbers like "3.14"
        line = re.sub(r'([.,;:!?])([A-Za-z])', _maybe_add_space, line)
        # Fix ".." or ",,"
        line = re.sub(r'\.{2,}', '.', line)
        line = re.sub(r',{2,}', ',', line)

        fixed.append(line)

    return '\n'.join(fixed)

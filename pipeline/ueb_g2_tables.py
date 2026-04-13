"""
UEB Grade 2 contraction tables.

BRF ASCII notation — each BRF character maps to braille dots.
Contractions are multi-character BRF sequences that expand to English words/parts.

Reference: "The Rules of Unified English Braille" (2013), ICEB.
"""

# ============================================================
# Alphabetic wordsigns (single letter = whole word when standalone)
# These are the same BRF letters but mean a word when "standing alone"
# (preceded and followed by space or punctuation)
# ============================================================

ALPHABETIC_WORDSIGNS = {
    'b': 'but',
    'c': 'can',
    'd': 'do',
    'e': 'every',
    'f': 'from',
    'g': 'go',
    'h': 'have',
    'j': 'just',
    'k': 'knowledge',
    'l': 'like',
    'm': 'more',
    'n': 'not',
    'p': 'people',
    'q': 'quite',
    'r': 'rather',
    's': 'so',
    't': 'that',
    'u': 'us',
    'v': 'very',
    'w': 'will',
    'x': 'it',
    'y': 'you',
    'z': 'as',
}

# ============================================================
# Strong wordsigns (single BRF char = whole word, always)
# ============================================================

STRONG_WORDSIGNS = {
    '!': 'the',     # dots 2346
    '&': 'and',     # dots 12346
    '=': 'for',     # dots 123456  (Note: in BRF context)
    '(': 'of',      # dots 12356
    '%': 'the',     # dots 146 (alternate)
    '?': 'the',     # dots 1456
    ':': 'the',     # dots 156
    '\\': 'ou',     # dots 1256
    '[': 'ow',      # dots 246
    ']': 'right',   # dots 12456
    '$': 'th',      # dots 1456
    '<': 'gh',      # dots 126
    '>': 'ar',      # dots 345
    '*': 'ch',      # dots 16
    '/': 'sh',      # dots 34
    '+': 'ing',     # dots 346
    '^': 'and',     # (alternate)
}

# ============================================================
# Strong contractions (groupsigns — can appear within words)
# These are always contracted regardless of position
# ============================================================

# Strong groupsigns that are ALWAYS contractions (no punctuation conflict)
STRONG_GROUPSIGNS_SAFE = {
    '&': 'and',
    '*': 'ch',
    '<': 'gh',
    '>': 'ar',
    '+': 'ing',
    '\\': 'ou',
    '|': 'ou',     # alternate BRF encoding for dots 1256
    '[': 'ow',
    ']': 'right',  # dots 12456
}

# Groupsigns that conflict with punctuation — only apply WITHIN words
# (between letters, not at word boundaries)
STRONG_GROUPSIGNS_CONTEXTUAL = {
    '!': 'the',
    '=': 'for',
    '(': 'of',
    '$': 'th',
    '/': 'sh',
    '%': 'the',
}

# ============================================================
# Strong groupsigns — multi-character BRF sequences
# ============================================================

MULTI_CHAR_CONTRACTIONS = {
    # Dot 4-5-6 prefix (} in BRF) — suffix groupsigns
    '}!': 'tion',
    '}n': 'ation',
    '}s': 'sion',
    '}y': 'ity',
    '}e': 'ment',
    '}t': 'ment',
    '}_': 'ound',
    '}l': 'less',
    '}o': 'ong',
    '}c': 'ence',
    '}a': 'ance',
    '}f': 'ful',
    '}+': 'ness',

    # Dot 5 prefix (" in BRF) — wordsigns and groupsigns
    '"!': 'there',
    '"?': 'where',
    '"e': 'ever',
    '"h': 'here',
    '"o': 'one',
    '"u': 'under',
    '"w': 'word',
    '".': 'upon',
    '"<': 'ought',
    '"c': 'cannot',
    '"k': 'know',
    '"l': 'lord',
    '"m': 'many',
    '"n': 'name',
    '"s': 'spirit',
    '"y': 'young',
    '"f': 'father',
    '"d': 'day',
    '">': 'right',
    '",': '',       # dot 5 + dot 6 = various, skip
    '"-': 'com',    # dot 5 + dots 36

    # Dot 5-6 prefix (; in BRF) — initial-letter contractions
    ';b': 'be',
    ';c': 'con',
    ';d': 'dis',
    ';e': 'en',
    ';i': 'in',

    # Dot 4-6 prefix (. in BRF) — groupsigns
    '.e': 'ed',
    '.r': 'er',
    '.s': 'es',

    # Dot 4 prefix (@ in BRF)
    '@e': 'ea',     # dots 4 + dots 15
    '@s': 'ss',     # dots 4 + dots 234

    # Double-letter combinations
    '7': '?',       # dots 2356 = question mark standalone
}

# ============================================================
# Lower wordsigns (dots in lower half of cell)
# Single BRF character standing alone = word
# ============================================================

# Lower-cell wordsigns — standalone only
LOWER_WORDSIGNS = {
    '5': 'enough',  # dots 26
    '9': 'was',     # dots 356
    '0': 'were',    # dots 2356
}

# Lower-cell groupsigns — within words
LOWER_GROUPSIGNS = {
    '1': 'ea',      # dots 2    (within word)
    '2': 'be',      # dots 23   (within word: "be-" prefix)
    '5': 'en',      # dots 26   (within word)
    '8': 'his',     # dots 236  (standalone = "his", within word = "")
    '9': 'was',     # dots 356  (standalone)
}

# ============================================================
# Final-letter groupsigns (} prefix + letter)
# ============================================================

FINAL_LETTER_GROUPSIGNS = {
    '}d': 'ound',
    '}e': 'ment',
    '}n': 'tion',
    '}s': 'sion',
    '}t': 'ment',
    '}y': 'ity',
}

# ============================================================
# Shortform words — abbreviated spellings
# These are special whole-word abbreviations
# ============================================================

SHORTFORMS = {
    'ab': 'about',
    'abv': 'above',
    'ac': 'according',
    'acr': 'across',
    'af': 'after',
    'afn': 'afternoon',
    'afw': 'afterward',
    'ag': 'again',
    'ag/': 'against',
    'al': 'also',
    'alm': 'almost',
    'alr': 'already',
    'alt': 'altogether',
    'al?': 'although',
    'alw': 'always',
    'bec': 'because',
    'bef': 'before',
    'beh': 'behind',
    'bel': 'below',
    'ben': 'beneath',
    'bes': 'beside',
    'bet': 'between',
    'bey': 'beyond',
    'bl': 'blind',
    'brl': 'braille',
    'cd': 'could',
    '*n': 'children',
    'dcl': 'declare',
    'dcg': 'deceiving',
    'dclg': 'declaring',
    'ei': 'either',
    'fst': 'first',
    'fr': 'friend',
    'gd': 'good',
    'grt': 'great',
    'hm': 'him',
    'hmf': 'himself',
    'imm': 'immediate',
    'xs': 'its',
    'xf': 'itself',
    'lr': 'letter',
    'll': 'little',
    'mst': 'must',
    'myf': 'myself',
    'nec': 'necessary',
    'nei': 'neither',
    'o\'c': "o'clock",
    'pd': 'paid',
    'p]ps': 'perhaps',
    'qk': 'quick',
    'rcv': 'receive',
    'rcvg': 'receiving',
    'rjc': 'rejoice',
    'rjcg': 'rejoicing',
    'sd': 'said',
    '/d': 'should',
    'sc': 'such',
    'td': 'today',
    'tgr': 'together',
    'tm': 'tomorrow',
    'tn': 'tonight',
    'wd': 'would',
    'yr': 'your',
    'yrf': 'yourself',
    'yrvs': 'yourselves',
}

"""
Shared similarity metrics used across all evaluation scripts.

Provides:
  - normalized_edit_similarity : 1 - (edit_distance / max_len)
  - chrf_score                : character n-gram F-score (simplified)
  - token_overlap_f1          : token-level precision/recall/F1
"""

from __future__ import annotations
from collections import Counter


def _edit_distance(a: str, b: str) -> int:
    """Standard Levenshtein distance (dynamic programming)."""
    n, m = len(a), len(b)
    if n == 0:
        return m
    if m == 0:
        return n
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        curr = [i] + [0] * m
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev = curr
    return prev[m]


def normalized_edit_similarity(a: str, b: str, *, strip_whitespace: bool = False,
                                strip_punctuation: bool = False) -> float:
    """Return 1 - edit_distance/max_len. Range [0, 1]."""
    if strip_whitespace:
        a = ''.join(a.split())
        b = ''.join(b.split())
    if strip_punctuation:
        import string
        table = str.maketrans('', '', string.punctuation)
        a = a.translate(table)
        b = b.translate(table)
    if not a and not b:
        return 1.0
    dist = _edit_distance(a, b)
    max_len = max(len(a), len(b))
    return 1.0 - dist / max_len


def _char_ngrams(text: str, n: int) -> Counter:
    return Counter(text[i:i + n] for i in range(len(text) - n + 1))


def chrf_score(reference: str, hypothesis: str, *, max_n: int = 6, beta: float = 2.0) -> float:
    """
    Simplified chrF score (character n-gram F-score).
    beta=2 weights recall twice as much as precision (standard chrF).
    """
    if not reference and not hypothesis:
        return 1.0
    if not reference or not hypothesis:
        return 0.0

    total_p, total_r = 0.0, 0.0
    count = 0
    for n in range(1, max_n + 1):
        ref_ngrams = _char_ngrams(reference, n)
        hyp_ngrams = _char_ngrams(hypothesis, n)
        if not ref_ngrams or not hyp_ngrams:
            continue
        overlap = sum((ref_ngrams & hyp_ngrams).values())
        precision = overlap / sum(hyp_ngrams.values()) if sum(hyp_ngrams.values()) > 0 else 0
        recall = overlap / sum(ref_ngrams.values()) if sum(ref_ngrams.values()) > 0 else 0
        total_p += precision
        total_r += recall
        count += 1

    if count == 0:
        return 0.0

    avg_p = total_p / count
    avg_r = total_r / count
    if avg_p + avg_r == 0:
        return 0.0

    beta_sq = beta ** 2
    f = (1 + beta_sq) * avg_p * avg_r / (beta_sq * avg_p + avg_r)
    return f


def token_overlap_f1(reference: str, hypothesis: str) -> dict:
    """Token-level overlap metrics. Returns dict with precision, recall, f1."""
    ref_tokens = Counter(reference.lower().split())
    hyp_tokens = Counter(hypothesis.lower().split())
    overlap = sum((ref_tokens & hyp_tokens).values())
    if overlap == 0:
        return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
    precision = overlap / sum(hyp_tokens.values())
    recall = overlap / sum(ref_tokens.values())
    f1 = 2 * precision * recall / (precision + recall)
    return {'precision': precision, 'recall': recall, 'f1': f1}

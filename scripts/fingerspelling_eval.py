"""Evaluate a fingerspelling classifier, person-independently or not at all.

The split is the whole point. A random split puts the same signer's hand in both
train and test, and the model learns that hand rather than the letter. Published
fingerspelling accuracies have been inflated this way for years. This harness
refuses to report a random split: every sample carries a signer id, and folds
are grouped by signer.

With no Korean fingerspelling dataset available, `--self-test` runs the harness
on synthetic keypoints — jamo prototypes plus per-signer hand-shape bias — to
show that the machinery works and, more usefully, what the two split strategies
do to the same data.

Usage:
    python scripts/fingerspelling_eval.py --self-test
    python scripts/fingerspelling_eval.py --data data/ksl/keypoints.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.fingerspelling import N_LANDMARKS, NearestCentroid, features  # noqa: E402

# Korean fingerspelling covers the jamo; this is the consonant set.
JAMO = list("ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ")


def synth(n_signers: int = 6, per_label: int = 8, seed: int = 0) -> tuple[np.ndarray, list[str], list[str]]:
    """Synthetic keypoints: a prototype per jamo, plus a per-signer bias.

    The signer bias is what makes the two split strategies differ. It is not
    noise — it is a systematic offset, the way one person's hand differs from
    another's, and it is exactly what a random split lets a model exploit.
    """
    rng = np.random.default_rng(seed)
    proto = {j: rng.normal(0, 1, (N_LANDMARKS, 3)) for j in JAMO}
    bias = {s: rng.normal(0, 0.55, (N_LANDMARKS, 3)) for s in range(n_signers)}

    X, y, g = [], [], []
    for s in range(n_signers):
        for j in JAMO:
            for _ in range(per_label):
                hand = proto[j] + bias[s] + rng.normal(0, 0.18, (N_LANDMARKS, 3))
                X.append(features(hand))
                y.append(j)
                g.append(f"signer{s}")
    return np.stack(X), y, g


def load(path: Path) -> tuple[np.ndarray, list[str], list[str]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    X = np.stack([features(np.asarray(r["landmarks"])) for r in raw["samples"]])
    y = [r["label"] for r in raw["samples"]]
    g = [str(r["signer"]) for r in raw["samples"]]
    return X, y, g


def evaluate(X: np.ndarray, y: list[str], groups: list[str], *, person_independent: bool,
             seed: int = 0) -> dict:
    y_arr = np.asarray(y)
    g_arr = np.asarray(groups)

    if person_independent:
        folds = [(g_arr != s, g_arr == s) for s in sorted(set(groups))]
    else:
        # Shown only for comparison. Never report this as the headline number.
        rng = np.random.default_rng(seed)
        idx = rng.permutation(len(y))
        folds = []
        for part in np.array_split(idx, len(set(groups))):
            test = np.zeros(len(y), bool)
            test[part] = True
            folds.append((~test, test))

    correct = total = 0
    confusion: Counter[tuple[str, str]] = Counter()
    for train_mask, test_mask in folds:
        if not train_mask.any() or not test_mask.any():
            continue
        model = NearestCentroid.fit(X[train_mask], list(y_arr[train_mask]))
        pred = model.predict(X[test_mask])
        for truth, guess in zip(y_arr[test_mask], pred):
            confusion[(truth, guess)] += 1
            correct += truth == guess
            total += 1

    labels = sorted(set(y))
    per_label = {}
    for lab in labels:
        tp = confusion[(lab, lab)]
        fp = sum(n for (t, p), n in confusion.items() if p == lab and t != lab)
        fn = sum(n for (t, p), n in confusion.items() if t == lab and p != lab)
        per_label[lab] = {
            "precision": tp / (tp + fp) if tp + fp else 0.0,
            "recall": tp / (tp + fn) if tp + fn else 0.0,
            "support": tp + fn,
        }

    macro_p = sum(v["precision"] for v in per_label.values()) / len(per_label)
    macro_r = sum(v["recall"] for v in per_label.values()) / len(per_label)
    return {
        "split": "person-independent" if person_independent else "random (inflated)",
        "folds": len(folds),
        "samples": total,
        "accuracy": correct / total if total else 0.0,
        "macro_precision": macro_p,
        "macro_recall": macro_r,
        "per_label": per_label,
        "top_confusions": [
            {"true": t, "pred": p, "n": n}
            for (t, p), n in confusion.most_common(40) if t != p
        ][:8],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Fingerspelling evaluation")
    ap.add_argument("--data", help="JSON with samples[].landmarks/.label/.signer")
    ap.add_argument("--self-test", action="store_true", help="run on synthetic keypoints")
    ap.add_argument("--output", default=str(PROJECT_ROOT / "docs" / "track-c-eval-results.json"))
    args = ap.parse_args()

    if args.data:
        X, y, g = load(Path(args.data))
        source = args.data
    elif args.self_test:
        X, y, g = synth()
        source = "synthetic (no Korean fingerspelling dataset available)"
    else:
        raise SystemExit("give --data or --self-test")

    print(f"source: {source}")
    print(f"samples {len(y)}, labels {len(set(y))}, signers {len(set(g))}\n")

    honest = evaluate(X, y, g, person_independent=True)
    inflated = evaluate(X, y, g, person_independent=False)

    for r in (honest, inflated):
        print(f"{r['split']:26s} accuracy {r['accuracy']:.3f}  "
              f"macro-P {r['macro_precision']:.3f}  macro-R {r['macro_recall']:.3f}")

    gap = inflated["accuracy"] - honest["accuracy"]
    print(f"\ninflation from splitting wrongly: {gap:+.3f}")
    if honest["top_confusions"]:
        print("\nmost confused pairs (person-independent):")
        for c in honest["top_confusions"][:5]:
            print(f"  {c['true']} -> {c['pred']}  {c['n']}")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps({"source": source, "person_independent": honest, "random_split": inflated},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()

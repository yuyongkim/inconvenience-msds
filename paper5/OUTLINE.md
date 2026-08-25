# Paper 5 — Outline (Draft v1)

## Working Title

**Person-Independent Evaluation for Korean Fingerspelling Recognition, and Why
the Split Is the Result**

## Where this sits in the series

Papers 1-4 are about braille and audio: getting written safety information to
people who cannot see it. This one changes modality entirely. It is about deaf
readers, sign language, and computer vision, and it shares only the underlying
premise — that technical terminology is where accessibility infrastructure
tends to stop.

That premise has a concrete form here. Chemical names have no registered sign,
so Korean Sign Language spells them with 지문자, one static hand shape per jamo.

## Scope, narrowed deliberately

An earlier attempt at continuous sign recognition did not reach useful accuracy
at amateur scale. The change that makes the problem tractable is not better
modelling but a smaller problem:

- single static hand shapes, not continuous signing
- MediaPipe keypoints, not raw pixels — dozens of dimensions instead of tens of
  thousands, which matters when data is the scarce resource

## The actual contribution

Not a recogniser. An evaluation protocol, and evidence for why it is needed.

A random train/test split puts the same signer's hand on both sides. The model
scores well by recognising the person, and the number says nothing about a new
user. Fingerspelling accuracies have been inflated this way for years, and the
inflation is invisible unless both splits are computed.

`scripts/fingerspelling_eval.py` groups folds by signer, computes the random
split too, and prints the gap. On synthetic keypoints with a per-signer hand
bias, the random split reads 4.2 points higher on identical data — and that is
a floor, because synthetic signer variation is milder than real hands.

The classifier is nearest centroid, chosen weak on purpose. A high-capacity
model on a small dataset memorises signers, which shows up as an excellent
person-dependent score and a person-independent collapse. A weak classifier
makes that visible rather than hiding it.

## Honest status: no dataset

**No evaluation on real Korean fingerspelling has been run.** AI Hub's Korean
Sign Language corpora sit behind registration and approval; the KETI corpus is
sentence-level, not fingerspelling; published Korean work uses privately
collected images.

Every number produced so far is synthetic. It demonstrates the harness runs and
quantifies the split effect. It is not recognition accuracy and the paper must
not present it as such.

## Target venue

Depends entirely on what data becomes available.

1. **ASSETS** — if a real dataset and a deaf-community consultation happen.
2. **LREC** — if the contribution stays a protocol plus a released dataset.
3. **A short methods note** — if neither, arguing the split point on synthetic
   evidence alone. Weakest option, but honest, and the argument stands.

## Status

| Component | State |
|---|---|
| Keypoint normalisation | implemented, `pipeline/fingerspelling.py` |
| Classifier | nearest centroid, implemented |
| Person-independent harness | implemented, enforces grouping |
| Split-inflation measurement | done on synthetic data |
| Real dataset | **none obtained** |
| Robustness (lighting, angle, skin tone, occlusion) | untested |
| Deaf-community consultation | none |

## What has to happen before submission

- **Data.** AI Hub approval, or a collection of 10-15 signers across all jamo.
  Person-independent evaluation needs signers, not samples: 5 signers with
  1,000 images each is weaker than 15 signers with 50.
- **Skin-tone measurement.** MediaPipe has documented variation across skin
  tones. A system that works worse for darker-skinned signers is a fairness
  failure, not a footnote, and we have not measured it.
- **A prior question, before any collection.** Whether deaf signers want a
  fingerspelling recogniser at all. A hearing-led project can build a
  technically sound tool for something nobody asked for, and the engineering
  being correct does not make the project worth doing.

## Drafted material

- `docs/track-c-fingerspelling-eval.md`
- `docs/track-c-limitations.md`
- `docs/track-c-eval-results.json`

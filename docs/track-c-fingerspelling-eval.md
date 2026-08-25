# Track C — fingerspelling recognition: method and evaluation protocol

## Why this scope

Technical terms have no registered sign. A chemical name in Korean Sign Language
is spelled out with 지문자, one static hand shape per jamo. That is a far smaller
problem than continuous signing: no segmentation, no grammar, no temporal
modelling. One shape, one label.

An earlier attempt at continuous motion recognition did not reach useful
accuracy at amateur scale. Narrowing to static hand shapes is the change that
makes the problem tractable, not better modelling.

## Why keypoints rather than pixels

MediaPipe already solves hand localisation and returns 21 landmarks per hand,
pretrained and free. Classifying 21 points is a problem in dozens of dimensions;
classifying raw frames is tens of thousands. The second needs orders of
magnitude more data to reach the same place, and the data is what we do not
have.

## Normalisation

This is where accuracy is won or lost, and it is easy to skip.

Raw landmarks encode three things that are not the letter: where the hand sits
in frame, how far it is from the camera, and how the wrist is rolled. All three
vary more between two recordings of the same letter than the letters vary
between each other. A classifier trained on unnormalised landmarks learns the
recording session.

`pipeline.fingerspelling.normalize` removes all three:

- translate so the wrist is the origin
- scale by palm width — index-knuckle to pinky-knuckle, which is stable across
  hand poses, unlike fingertip spread, which changes with the letter
- rotate so the wrist-to-middle-knuckle axis points along +y

## The split is the result

A random train/test split puts the same signer's hand on both sides. The model
then scores well by recognising the person, and the number means nothing for a
new user. Fingerspelling accuracies in the literature have been inflated this
way for years.

`scripts/fingerspelling_eval.py` groups folds by signer and holds each signer
out in turn. It computes the random split too, and prints both, so the
difference is visible rather than assumed.

On synthetic keypoints with a per-signer hand-shape bias:

| Split | Accuracy | Macro precision | Macro recall |
|---|---:|---:|---:|
| Person-independent | 0.908 | 0.925 | 0.908 |
| Random | 0.949 | 0.955 | 0.949 |

The random split reads 4.2 points higher on identical data. That gap is the
whole argument for the protocol, and it is a floor: the synthetic signer bias is
milder and more uniform than real hands.

## Classifier

Nearest centroid, one centroid per jamo. Chosen deliberately over a trained
network. With the data a small collection can produce, a high-capacity model
memorises signers rather than letters, which shows up as an excellent
person-dependent score and a person-independent one that collapses. A weak
classifier makes that failure visible instead of hiding it.

## No dataset

**No evaluation on real Korean fingerspelling has been run, because no dataset
was obtainable.** AI Hub hosts Korean Sign Language data behind registration and
approval. The KETI sentence-level corpus is the only widely cited Korean set and
is not fingerspelling. Published Korean fingerspelling work uses privately
collected images.

The numbers above are from synthetic keypoints. They demonstrate that the
harness runs and quantify the split effect. **They are not recognition accuracy
and must not be cited as such.**

What would change this:

- AI Hub approval for the sign language corpora, then checking whether any
  contains isolated jamo.
- A small collection: 10-15 signers, all jamo, several takes each, recorded at
  varying distance and lighting. Person-independent evaluation needs signers,
  not samples — 5 signers with 1,000 images each is a weaker dataset than 15
  signers with 50.

## Reproduction

```
python scripts/fingerspelling_eval.py --self-test
python scripts/fingerspelling_eval.py --data data/ksl/keypoints.json
```

The data file expects `samples[].landmarks` (21x3), `.label`, and `.signer`.
The signer field is required; the harness cannot do its job without it.

## Expert-review candidates

Scoped to single items, for a later consultation:

- Whether the jamo inventory used here matches what deaf signers actually
  produce when spelling technical terms, including any shapes that differ by
  region or generation.
- Whether static shapes are sufficient, or whether some Korean jamo require
  movement and therefore fall outside this scope entirely.
- Collection protocol before recording anything: consent, signer diversity,
  and whether a hearing-led collection is appropriate at all.

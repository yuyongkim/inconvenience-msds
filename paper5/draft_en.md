# Person-Independent Evaluation for Korean Fingerspelling Recognition, and Why the Split Is the Result

Yuyong Kim
University of Wisconsin-Madison, Madison, WI 53706, USA
Email: ykim288@wisc.edu
ORCID: 0009-0006-4842-666X

---

## Abstract

**Purpose.** Technical terms such as chemical names have no registered sign, so Korean Sign Language spells them with 지문자, one static hand shape per jamo. This report presents an evaluation protocol for static fingerspelling recognition and shows quantitatively that person-independent splitting is not optional.

**Methods.** We classify the 21 hand landmarks MediaPipe produces rather than raw pixels. We define a normalisation that removes position, scale and in-plane rotation from the landmarks, and implement a nearest-centroid classifier with one centroid per jamo. The evaluation harness groups folds by signer and computes the random split alongside for comparison. We also audited the column names of nine public sign-alphabet datasets to see whether they record who signed each sample.

**Results.** On synthetic keypoints carrying a per-signer hand-shape bias, the random split reported accuracy 4.2 points higher than the person-independent split on identical data (0.949 against 0.908). That gap is a floor, because the synthetic bias is more uniform than variation between real hands. Of the seven public datasets whose schema resolved, none carries a signer, subject or participant column.

**Conclusions.** No Korean fingerspelling dataset was obtainable, so **recognition accuracy was not measured.** Every figure reported here is synthetic and demonstrates only that the harness runs and how large the split effect is. The contribution is the evaluation protocol and the evidence for needing it, not a recogniser. Because the public datasets omit signer identity, a person-independent split is not expressible on them at all, which is the practical reason the protocol keeps going unapplied.

**Keywords:** Korean Sign Language; fingerspelling; person-independent evaluation; MediaPipe; accessibility; evaluation methodology

---

## 1. Introduction

Earlier papers in this series [1] concern braille and audio: delivering written safety information to people who cannot see it. This paper changes modality. It concerns deaf readers, sign language and computer vision, and shares only one premise — that accessibility infrastructure tends to stop at technical terminology.

Here that premise takes a concrete form. Chemical names have no registered sign, so Korean Sign Language spells them out.

### 1.1 A deliberately narrowed scope

An earlier attempt at continuous sign recognition did not reach useful accuracy at amateur scale. What makes the problem tractable is not better modelling but a smaller problem.

- Single static hand shapes rather than continuous signing: no segmentation, no grammar, no temporal modelling.
- MediaPipe keypoints rather than raw pixels: dozens of dimensions instead of tens of thousands, which is decisive when data is the scarce resource.

## 2. Methods

### 2.1 Normalisation

This is where accuracy is won or lost, and it is easy to skip.

Raw landmarks encode three things that are not the letter: where the hand sits in frame, how far it is from the camera, and how the wrist is rolled. All three vary more between two recordings of the same letter than the letters vary between each other. A classifier trained on unnormalised landmarks learns the recording session.

Normalisation removes all three:

1. translate so the wrist is the origin;
2. scale by palm width (index knuckle to pinky knuckle), which is stable across hand poses, unlike fingertip spread, which changes with the letter being signed;
3. rotate so the wrist-to-middle-knuckle axis points along +y, removing camera roll and wrist tilt.

### 2.2 Classifier

We use nearest centroid, one centroid per jamo, chosen over a trained network deliberately. With the data a small collection can produce, a high-capacity model memorises signers rather than letters, which appears as an excellent person-dependent score and a person-independent collapse. A weak classifier makes that failure visible instead of hiding it.

### 2.3 Evaluation protocol

A random train/test split places the same signer's hand on both sides. The model then scores well by recognising the person, and the number says nothing about a new user.

The harness groups folds by signer and holds each signer out in turn. It computes the random split as well and prints both, so the difference is observed rather than assumed.

## 3. Results

**Table 1.** Two splits over identical data (synthetic keypoints; 6 signers, 14 jamo, 672 samples)

| Split | Accuracy | Macro precision | Macro recall |
|---|---:|---:|---:|
| Person-independent | 0.908 | 0.925 | 0.908 |
| Random | 0.949 | 0.955 | 0.949 |

The random split reads 4.2 points higher on identical data (Fig. 1). That gap is the whole argument for the protocol, and it is a floor: the synthetic signer bias is milder and more uniform than variation between real hands.

## 4. Absence of a dataset

**No evaluation on real Korean fingerspelling was performed.** No dataset was obtainable.

- AI Hub's Korean Sign Language corpora require registration and approval.
- The widely cited KETI corpus is sentence-level, not fingerspelling.
- Published Korean fingerspelling work uses privately collected imagery.

All figures in Section 3 come from synthetic keypoints. They show that the harness runs and quantify the split effect. **They are not recognition accuracy and must not be cited as such.**

### 4.1 The signer field is missing, not merely unused

A protocol is only worth arguing for if the data can carry it, so we checked
whether public fingerspelling datasets record who signed each sample. We queried
the Hugging Face datasets API for the sign-alphabet corpora a practitioner would
reach for first, and read their column names.

**Table 2.** Columns of public fingerspelling datasets. Seven of nine repositories
resolved; the remaining two are unparsed by the datasets server.

| Dataset | Columns | Signer field |
|---|---|---|
| Voxel51/American-Sign-Language-MNIST | image, label | no |
| Marxulia/asl_sign_languages_alphabets_v03 | image, label | no |
| shpouladi/American-Sign-Language-Dataset | video | no |
| just-me7ss/American-Sign-Language-Dataset | video | no |
| akasheroor/American-Sign-Language-Dataset | video | no |
| ZahidYasinMittha/American-Sign-Language-Dataset | video | no |
| silentone0725/Indian_Sign_Language_Data.gov_Rencoded | label, video | no |

None of them carries a signer, subject, or participant column. The largest of
them, the 34,627-sample ASL-MNIST derived from the standard Kaggle release, is
the benchmark most fingerspelling papers report on, and it stores only the image
and its letter.

This changes what Section 3 is claiming. A person-independent split on these
datasets has not merely been neglected: it is **not expressible**, because the
grouping variable was never recorded. Every accuracy published on them is a
random split by construction, and therefore carries at least the inflation
measured in Table 1, whether or not its authors chose the protocol.

It also sets the minimum requirement for any Korean fingerspelling collection
that follows. Signer identity costs one integer column and cannot be recovered
afterwards. Omitting it does not make a dataset smaller; it makes every result
computed from it unfalsifiable in the one dimension that matters for a system
meant to work on a person it has never seen.

## 5. Limitations

Written before results rather than after, so the list is not shaped by what happened to work.

### 5.1 Robustness untested

- **Lighting.** MediaPipe degrades in low light and under strong directional light. Untested.
- **Hand angle.** Landmarks are 3D, but a shape seen edge-on loses the information separating similar jamo. Normalisation removes in-plane roll only.
- **Skin tone.** MediaPipe's hand detector has documented performance variation across skin tones. We have not measured it, and a system that works worse for darker-skinned signers is a fairness failure rather than a footnote.
- **Hand size.** Palm-width scaling should cover adult variation; children's hands are unverified.
- **Occlusion.** Fingers crossing or hiding each other, which several jamo require, yields unreliable landmarks. Not handled.

### 5.2 Scope boundaries

- Static shapes only. Any jamo requiring movement is out of scope, and whether Korean fingerspelling contains such jamo is a question we have not answered — it bounds how much of the alphabet this can cover.
- Segmenting a fingerspelled word into letters, and sentence-level sign recognition, are both out of scope.

### 5.3 Method limitations

- Nearest centroid assumes each jamo forms one cluster. A jamo signed two legitimate ways is modelled as one blurred centroid and scores poorly for reasons resembling noise.
- Palm-width normalisation fails when the palm is edge-on and the two knuckles project onto nearly the same point. A fallback exists but is weaker.
- No confidence output: the classifier always returns a label, including for a hand shape that is not a jamo.

### 5.4 Who has not been consulted

No deaf signer, sign language linguist or interpreter has reviewed any of this — not the jamo inventory, not the assumption that static shapes suffice, not whether a fingerspelling recogniser is wanted.

That last question should be asked first. A hearing-led project can build a technically sound recogniser for something the deaf community has no use for, and the engineering being correct does not make the project worth doing.


The consultation is written out as a protocol rather than left as an intention: `docs/paper5-consultation-protocol.md` fixes the questions, the three constituencies to ask, the consent steps, and — before any answer is heard — what each possible answer does to this paper. Committing the interpretation in advance is the part that matters, because a question asked after the analysis is chosen can only ratify it. If the answer is that the tool is not wanted, the protocol records that this report stays a protocol paper and the negative result is published as a finding.

## 6. Conclusion

The contribution is an evaluation protocol, not a recogniser. By enforcing signer-grouped folds and printing the random-split difference alongside, inflation becomes something observed rather than assumed. Evaluation on real data awaits a dataset. The datasets that exist cannot support the protocol, since none of them records signer identity, so the requirement lands on collection rather than on analysis: one integer column, written down at capture time, or the question stays unanswerable.

## Reproduction

```
python scripts/fingerspelling_eval.py --self-test
python scripts/fingerspelling_eval.py --data data/ksl/keypoints.json
python scripts/dataset_signer_audit.py
```

The data file requires `samples[].landmarks` (21×3), `.label` and `.signer`. The signer field is mandatory; without it the harness cannot do its job.

`dataset_signer_audit.py` queries the Hugging Face datasets API and writes `docs/track-c-dataset-audit.json`. It needs no token. Table 2 is that file.

## References

[1] Kim, Y. (2026). KOSHA-Braille: infrastructure-grade accessibility for Korean chemical safety information. *Universal Access in the Information Society*, 25, 116. https://doi.org/10.1007/s10209-026-01381-0

[2] Zhang, F. et al. (2020). MediaPipe Hands: on-device real-time hand tracking. *CVPR Workshop on Computer Vision for Augmented and Virtual Reality*.

[3] Ko, S. et al. (2019). Neural sign language translation based on human keypoint estimation. *Applied Sciences*, 9(13), 2683.

---

## Figures

**Fig. 1** Scores under the two splits over identical data. The vertical axis is truncated at 0.85. Synthetic keypoints; not recognition accuracy. (`figures/Fig1.png`)

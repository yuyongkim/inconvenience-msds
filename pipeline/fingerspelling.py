"""Hand-shape features for Korean fingerspelling, and a classifier over them.

Terms like chemical names have no registered sign, so Korean Sign Language
spells them with 지문자 — static hand shapes for individual jamo. That makes the
recognition problem much smaller than continuous signing: one shape, one label,
no segmentation, no grammar.

The pipeline deliberately does not classify pixels. MediaPipe already solves
hand localisation and gives 21 landmarks; classifying those is a problem with
dozens of dimensions instead of tens of thousands, and it needs far less data.
An earlier attempt at continuous motion recognition failed at amateur scale for
exactly the reason this avoids.

Normalisation is where the accuracy comes from or does not. Raw landmark
coordinates encode where the hand is in frame, how big it is, and how the camera
is rotated — none of which is the letter. `normalize` removes all three, so two
people signing the same jamo at different distances land in the same place.

No trained model ships here. There is no public Korean fingerspelling dataset we
can download; see docs/track-c-fingerspelling-eval.md.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# MediaPipe hand landmark indices.
WRIST = 0
INDEX_MCP = 5
MIDDLE_MCP = 9
PINKY_MCP = 17
N_LANDMARKS = 21


def normalize(landmarks: np.ndarray) -> np.ndarray:
    """Put a hand into a canonical frame: origin, scale, rotation removed.

    Takes (21, 3) landmarks, returns (21, 3).

    Without this a classifier learns the recording setup. Hand position in frame
    and distance from the camera vary far more between takes than the letters do
    between each other, so an unnormalised model scores well on its own
    recording session and collapses on anyone else's.
    """
    pts = np.asarray(landmarks, dtype=np.float64).reshape(N_LANDMARKS, -1)[:, :3].copy()

    # Origin at the wrist.
    pts -= pts[WRIST]

    # Scale by palm width, which is stable across hand poses. Finger-tip
    # distances are not: they change with the letter being signed.
    palm = np.linalg.norm(pts[PINKY_MCP] - pts[INDEX_MCP])
    if palm < 1e-6:
        palm = np.linalg.norm(pts[MIDDLE_MCP]) or 1.0
    pts /= palm

    # Rotate so the wrist-to-middle-knuckle axis points along +y. This removes
    # in-plane camera roll and how the signer happens to tilt their wrist.
    axis = pts[MIDDLE_MCP][:2]
    norm = np.linalg.norm(axis)
    if norm > 1e-6:
        cos, sin = axis[1] / norm, -axis[0] / norm
        rot = np.array([[cos, -sin], [sin, cos]])
        pts[:, :2] = pts[:, :2] @ rot.T
    return pts


def features(landmarks: np.ndarray) -> np.ndarray:
    """Flatten a normalised hand into a feature vector."""
    return normalize(landmarks).reshape(-1)


@dataclass
class NearestCentroid:
    """One centroid per jamo, nearest wins.

    Chosen over a trained network on purpose. With the amount of data a small
    collection can produce, a high-capacity model memorises signers rather than
    letters, and the person-independent score falls apart while the
    person-dependent one looks excellent.
    """

    labels: list[str]
    centroids: np.ndarray          # (n_labels, n_features)

    @classmethod
    def fit(cls, X: np.ndarray, y: list[str]) -> "NearestCentroid":
        labels = sorted(set(y))
        cents = np.stack([np.asarray(X)[[i for i, l in enumerate(y) if l == lab]].mean(axis=0)
                          for lab in labels])
        return cls(labels=labels, centroids=cents)

    def predict(self, X: np.ndarray) -> list[str]:
        X = np.atleast_2d(np.asarray(X))
        d = np.linalg.norm(X[:, None, :] - self.centroids[None, :, :], axis=2)
        return [self.labels[i] for i in d.argmin(axis=1)]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"labels": self.labels, "centroids": self.centroids.tolist()}),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> "NearestCentroid":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(labels=raw["labels"], centroids=np.asarray(raw["centroids"]))


def extract_from_image(image_path: str | Path, model_path: str | Path | None = None) -> np.ndarray | None:
    """Landmarks for the first hand found, or None.

    Needs the MediaPipe hand landmarker bundle; `model_path` points at the
    downloaded `.task` file.
    """
    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    if model_path is None or not Path(model_path).exists():
        raise FileNotFoundError(
            "hand_landmarker.task not found. Download it from "
            "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        )

    img = cv2.imread(str(image_path))
    if img is None:
        return None
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    opts = vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(model_path)),
        num_hands=1,
    )
    with vision.HandLandmarker.create_from_options(opts) as landmarker:
        result = landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    if not result.hand_landmarks:
        return None
    hand = result.hand_landmarks[0]
    return np.array([[p.x, p.y, p.z] for p in hand], dtype=np.float64)

"""Module 1 preprocessing: handwriting images -> model-ready tensors.

Dataset ships pre-cleaned 28x28 grayscale images with its own Train/Test split
(Normal/Reversal/Corrected). We respect that split: Test is held out untouched,
Train is further split into train/val.
"""
import csv
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split

from ..common.paths import RAW, PROCESSED, ensure
from ..common.logging_utils import get_logger

log = get_logger(__name__)
SRC = RAW / "m1_dyslexia_handwriting"
DST = PROCESSED / "m1_handwriting"
CLASSES = ["normal", "reversal", "corrected"]
FOLDER_TO_CLASS = {"Normal": "normal", "Reversal": "reversal", "Corrected": "corrected"}
IMG = 64


def preprocess_image(path: Path) -> np.ndarray:
    import cv2

    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"unreadable: {path}")
    # source is already clean 28x28 - just upscale to the model's input size
    interp = cv2.INTER_CUBIC if IMG > img.shape[0] else cv2.INTER_AREA
    img = cv2.resize(img, (IMG, IMG), interpolation=interp)
    return img.astype(np.float32) / 255.0


def load_split(split_name: str) -> tuple[list[np.ndarray], list[int], list[tuple[str, str]]]:
    X, y, manifest = [], [], []
    for folder_name, cls_name in FOLDER_TO_CLASS.items():
        label_idx = CLASSES.index(cls_name)
        folder = SRC / split_name / folder_name
        if not folder.exists():
            log.warning("missing %s - check the extracted layout", folder)
            continue
        for p in sorted(folder.glob("*.png")):
            try:
                X.append(preprocess_image(p))
                y.append(label_idx)
                manifest.append((str(p), cls_name))
            except ValueError as exc:
                log.warning("%s", exc)
    return X, y, manifest


def build() -> None:
    ensure(DST)

    X_train_full, y_train_full, manifest_train = load_split("Train")
    X_test, y_test, manifest_test = load_split("Test")

    X_train_full = np.stack(X_train_full)[:, None, :, :]
    y_train_full = np.array(y_train_full)
    X_test = np.stack(X_test)[:, None, :, :]
    y_test = np.array(y_test)

    log.info("train pool: %d | test (held out): %d | class counts (train) %s",
             len(y_train_full), len(y_test), np.bincount(y_train_full).tolist())

    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train_full, y_train_full, test_size=0.15,
        stratify=y_train_full, random_state=42)

    np.savez_compressed(DST / "m1_data.npz",
                        X_train=X_tr, y_train=y_tr,
                        X_val=X_val, y_val=y_val,
                        X_test=X_test, y_test=y_test,
                        classes=np.array(CLASSES))
    with open(DST / "manifest.csv", "w", newline="") as f:
        csv.writer(f).writerows([("path", "label"), *manifest_train, *manifest_test])
    log.info("saved -> %s", DST / "m1_data.npz")


if __name__ == "__main__":
    build()
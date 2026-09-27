"""EMNIST 'letters' CSV -> pretraining tensors for the M1 CNN.

The 'letters' split merges upper/lower case into 26 classes, labelled 1-26
(not 0-25), and images are stored transposed relative to normal reading
orientation. Both need correcting before use.
"""
import numpy as np
import pandas as pd
import cv2

from ..common.paths import RAW, PROCESSED, ensure
from ..common.logging_utils import get_logger

log = get_logger(__name__)
SRC = RAW / "m1_emnist"
DST = PROCESSED / "m1_emnist"
IMG = 32


def _rows_to_images(df: pd.DataFrame) -> np.ndarray:
    pixels = df.iloc[:, 1:].to_numpy(dtype=np.float32) / 255.0
    imgs = pixels.reshape(-1, 28, 28)
    imgs = np.transpose(imgs, (0, 2, 1))          # fix EMNIST's stored orientation
    resized = np.stack([cv2.resize(im, (IMG, IMG), interpolation=cv2.INTER_AREA)
                        for im in imgs])
    return resized[:, None, :, :]


def build(max_rows: int | None = None) -> None:
    ensure(DST)
    train_df = pd.read_csv(SRC / "emnist-letters-train.csv", header=None, nrows=max_rows)
    test_df = pd.read_csv(SRC / "emnist-letters-test.csv", header=None, nrows=max_rows)

    X_train = _rows_to_images(train_df)
    y_train = train_df.iloc[:, 0].to_numpy() - 1   # labels are 1-26 -> 0-25
    X_test = _rows_to_images(test_df)
    y_test = test_df.iloc[:, 0].to_numpy() - 1

    np.savez_compressed(DST / "emnist_letters.npz",
                        X_train=X_train, y_train=y_train,
                        X_test=X_test, y_test=y_test)
    log.info("EMNIST letters: %d train, %d test, 26 classes -> %s",
             len(y_train), len(y_test), DST / "emnist_letters.npz")


if __name__ == "__main__":
    build()
"""Module 7 feature builder: per-word synthetic error records -> one row per session.

Trains M7 on synthetic utterances (each synthetic "sentence" = one reading session).
Label is derived from severity: mild=0 (typical), moderate/severe=1 (at-risk indicator),
which gives M7 a genuine binary target to learn from without needing real NNCES data.
"""
import json
from collections import Counter
import pandas as pd

from ..common.paths import PROCESSED, SYNTHETIC, ensure
from ..common.logging_utils import get_logger

log = get_logger(__name__)
SRC = SYNTHETIC / "reading_errors" / "synthetic_errors.jsonl"
DST = PROCESSED / "m7_risk"

SEVERITY_TO_LABEL = {"mild": 0, "moderate": 1, "severe": 1}


def build() -> None:
    ensure(DST)
    rows = []
    for i, line in enumerate(SRC.read_text(encoding="utf-8").splitlines()):
        if not line:
            continue
        utt = json.loads(line)
        words = utt.get("words", [])
        if not words:
            continue
        n = len(words)
        counts = Counter(w["label"] for w in words)
        durations = [w["word_duration"] for w in words]
        long_words = [w for w in words if w["target_len"] > 6]
        long_word_errors = sum(1 for w in long_words if w["label"] != "correct")

        rows.append({
            "utt_id": f"synth_{i}",
            "wpm": 60.0 / (sum(durations) / n) if n else 0.0,  # approx from mean word duration
            "accuracy": counts.get("correct", 0) / n,
            "error_rate": 1 - counts.get("correct", 0) / n,
            "substitution_rate": counts.get("mispronunciation", 0) / n,
            "omission_rate": counts.get("omission", 0) / n,
            "reversal_rate": counts.get("reversal", 0) / n,
            "mean_pause_ms": 0.0,  # not modeled in synthetic data - real pilot data will fill this in later
            "pause_count_per_100w": 0.0,
            "long_word_error_rate": long_word_errors / len(long_words) if long_words else 0.0,
            "self_correction_rate": 0.0,  # not modeled synthetically
            "label": SEVERITY_TO_LABEL[utt["severity"]],
        })

    out = pd.DataFrame(rows)
    out.to_csv(DST / "session_features.csv", index=False)
    log.info("built %d session feature rows -> %s (label balance: %s)",
             len(out), DST / "session_features.csv", out["label"].value_counts().to_dict())


if __name__ == "__main__":
    build()
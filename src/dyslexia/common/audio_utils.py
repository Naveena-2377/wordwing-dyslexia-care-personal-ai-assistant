import numpy as np


def load_audio(path: str, sr: int = 16000):
    import librosa

    y, _ = librosa.load(path, sr=sr, mono=True)
    return y, sr


def trim_silence(y: np.ndarray, top_db: int = 30) -> np.ndarray:
    import librosa

    trimmed, _ = librosa.effects.trim(y, top_db=top_db)
    return trimmed


def normalize_loudness(y: np.ndarray) -> np.ndarray:
    peak = np.abs(y).max()
    return y / peak if peak > 0 else y


def pause_statistics(word_timestamps: list[dict]) -> dict:
    """word_timestamps: [{'word':..,'start':..,'end':..}, ...] from Whisper."""
    if len(word_timestamps) < 2:
        return {"mean_pause_ms": 0.0, "pause_count": 0, "max_pause_ms": 0.0}
    gaps = [
        (word_timestamps[i + 1]["start"] - word_timestamps[i]["end"]) * 1000
        for i in range(len(word_timestamps) - 1)
    ]
    gaps = [g for g in gaps if g > 0]
    return {
        "mean_pause_ms": float(np.mean(gaps)) if gaps else 0.0,
        "pause_count": int(sum(g > 250 for g in gaps)),
        "max_pause_ms": float(max(gaps)) if gaps else 0.0,
    }

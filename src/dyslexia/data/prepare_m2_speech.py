"""Module 2 preprocessing: children's read-aloud audio -> aligned error records.

Steps: resample 16k mono -> trim silence -> loudness normalise -> VAD segment
-> Whisper transcribe with word timestamps -> align vs target text ->
emit one row per target word with its operation label + timing features.
"""
import json
from pathlib import Path

from ..common.paths import RAW, PROCESSED, ensure
from ..common.audio_utils import load_audio, trim_silence, normalize_loudness
from ..common.text_utils import tokenize, is_reversal_error
from ..common.alignment import align
from ..common.logging_utils import get_logger

log = get_logger(__name__)
SRC = RAW / "m2_nnces"
DST = PROCESSED / "m2_nnces"


def transcribe(audio_path: Path, model) -> dict:
    result = model.transcribe(str(audio_path), word_timestamps=True, language="en")
    words = [
        {"word": w["word"].strip(), "start": w["start"], "end": w["end"],
         "prob": w.get("probability", 1.0)}
        for seg in result["segments"] for w in seg.get("words", [])
    ]
    return {"text": result["text"], "words": words}


def label_pair(pair, spoken_meta: dict | None) -> str:
    if pair.op == "match":
        duration = (spoken_meta or {}).get("duration", 0.0)
        return "slow_decoding" if duration > 1.2 else "correct"
    if pair.op == "substitution":
        if is_reversal_error(pair.target or "", pair.spoken or ""):
            return "reversal"
        if pair.target and pair.spoken and pair.target[0] == pair.spoken[0]:
            return "mispronunciation"
        return "substitution"
    return pair.op  # omission | insertion


def build(limit: int | None = None) -> None:
    import whisper

    ensure(DST)
    model = whisper.load_model("small")
    rows = []
    # expects pairs: <stem>.wav + <stem>.txt (the prompt the child was asked to read)
    for audio_path in sorted(SRC.rglob("*.wav"))[:limit]:
        target_file = audio_path.with_suffix(".txt")
        if not target_file.exists():
            continue
        y, sr = load_audio(str(audio_path))
        y = normalize_loudness(trim_silence(y))
        duration_s = len(y) / sr

        hyp = transcribe(audio_path, model)
        target_tokens = tokenize(target_file.read_text(encoding="utf-8"))
        spoken_tokens = tokenize(hyp["text"])
        pairs = align(target_tokens, spoken_tokens)

        wpm = len(spoken_tokens) / (duration_s / 60) if duration_s else 0.0
        for k, pair in enumerate(pairs):
            meta = hyp["words"][k] if k < len(hyp["words"]) else None
            if meta:
                meta["duration"] = meta["end"] - meta["start"]
            rows.append({
                "utt_id": audio_path.stem,
                "position": k,
                "target": pair.target,
                "spoken": pair.spoken,
                "op": pair.op,
                "label": label_pair(pair, meta),
                "word_duration": (meta or {}).get("duration", 0.0),
                "asr_prob": (meta or {}).get("prob", 0.0),
                "target_len": len(pair.target or ""),
                "utt_wpm": wpm,
            })

    (DST / "aligned_errors.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows))
    log.info("wrote %d aligned word records -> %s", len(rows), DST)


if __name__ == "__main__":
    build()

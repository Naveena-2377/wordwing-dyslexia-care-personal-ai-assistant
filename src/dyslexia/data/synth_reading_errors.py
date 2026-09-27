"""Synthetic dyslexia-style error generator.

There is no large labelled corpus of dyslexic reading errors, so you build one:
take clean sentences, inject known error types with controlled probabilities,
and keep the injected type as the ground-truth label. Train on synthetic,
validate on synthetic, TEST ON REAL recordings only.
"""
import json
import random
from pathlib import Path

from ..common.paths import PROCESSED, SYNTHETIC, ensure
from ..common.text_utils import tokenize
from ..common.logging_utils import get_logger

log = get_logger(__name__)
DST = SYNTHETIC / "reading_errors"

REVERSAL_MAP = {"b": "d", "d": "b", "p": "q", "q": "p", "m": "w", "w": "m",
                "n": "u", "u": "n"}
FUNCTION_WORDS = {"the", "a", "an", "of", "to", "in", "is", "and", "it", "on", "at"}
PHONETIC_SUBS = [("ph", "f"), ("tion", "shun"), ("ough", "uf"), ("ck", "k"),
                 ("wh", "w"), ("kn", "n"), ("th", "d")]


def _duration(label: str) -> float:
    base = random.gauss(1.05, 0.45) if label == "slow_decoding" else random.gauss(0.5, 0.28)
    return round(max(0.12, base), 2)


def _asr_prob(label: str) -> float:
    base = random.gauss(0.62, 0.22) if label != "correct" else random.gauss(0.88, 0.14)
    return round(min(0.99, max(0.05, base)), 2)


def inject_reversal(word: str) -> str | None:
    idxs = [i for i, ch in enumerate(word) if ch in REVERSAL_MAP]
    if not idxs:
        return None
    i = random.choice(idxs)
    return word[:i] + REVERSAL_MAP[word[i]] + word[i + 1:]


def inject_transposition(word: str) -> str | None:
    if len(word) < 4:
        return None
    i = random.randint(0, len(word) - 2)
    return word[:i] + word[i + 1] + word[i] + word[i + 2:]


def inject_phonetic(word: str) -> str | None:
    for a, b in PHONETIC_SUBS:
        if a in word:
            return word.replace(a, b, 1)
    return None


def corrupt_sentence(sentence: str, rates: dict) -> list[dict]:
    tokens = tokenize(sentence)
    records = []
    for pos, tok in enumerate(tokens):
        roll = random.random()
        label, spoken = "correct", tok
        if roll < rates["reversal"]:
            out = inject_reversal(tok)
            if out:
                label, spoken = "reversal", out
        elif roll < rates["reversal"] + rates["omission"] and tok in FUNCTION_WORDS:
            label, spoken = "omission", None
        elif roll < rates["reversal"] + rates["omission"] + rates["mispronunciation"]:
            out = inject_phonetic(tok) or inject_transposition(tok)
            if out:
                label, spoken = "mispronunciation", out
        elif roll < sum(rates.values()) and len(tok) > 6:
            label = "slow_decoding"
        records.append({
    "position": pos, "target": tok, "spoken": spoken, "label": label,
    "target_len": len(tok),
    "word_duration": _duration(label),
    "asr_prob": _asr_prob(label),
    })
    return records


def build(corpus: Path | None = None, n_sentences: int = 20000,
          severity: str = "mixed") -> None:
    ensure(DST)
    profiles = {
        "mild":     {"reversal": 0.03, "omission": 0.03, "mispronunciation": 0.04,
                     "slow_decoding": 0.05},
        "moderate": {"reversal": 0.08, "omission": 0.07, "mispronunciation": 0.09,
                     "slow_decoding": 0.10},
        "severe":   {"reversal": 0.15, "omission": 0.12, "mispronunciation": 0.15,
                     "slow_decoding": 0.18},
    }
    corpus = corpus or (PROCESSED / "m3_wikilarge" / "simple_sentences.txt")
    sentences = corpus.read_text(encoding="utf-8").splitlines()[:n_sentences] if corpus.exists() else [
        "the cat sat on the mat", "plants use sunlight to make their food"]

    out = []
    for s in sentences:
        prof = random.choice(list(profiles)) if severity == "mixed" else severity
        recs = corrupt_sentence(s, profiles[prof])
        out.append({"sentence": s, "severity": prof, "words": recs})

    (DST / "synthetic_errors.jsonl").write_text(
        "\n".join(json.dumps(o) for o in out))
    log.info("generated %d synthetic utterances -> %s", len(out), DST)


if __name__ == "__main__":
    build()

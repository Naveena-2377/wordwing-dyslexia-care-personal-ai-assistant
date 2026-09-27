"""End-to-end inference pipeline: one reading session in, a full profile out.

input  : audio of the child reading + the target text (or an uploaded page)
output : per-word errors, session features, risk band, next exercise
"""
from dataclasses import dataclass, asdict
from pathlib import Path

from ..common.text_utils import tokenize
from ..common.alignment import align
from ..common.audio_utils import pause_statistics
from ..common.logging_utils import get_logger

log = get_logger(__name__)


@dataclass
class SessionResult:
    utt_id: str
    wpm: float
    accuracy: float
    word_errors: list[dict]
    error_rates: dict[str, float]
    risk_score: float
    risk_band: str
    next_exercise: str
    highlights: list[dict]          # word spans for the UI to colour


class ReadingSessionPipeline:
    def __init__(self, error_clf, risk_scorer, coach, asr):
        self.error_clf = error_clf
        self.risk_scorer = risk_scorer
        self.coach = coach
        self.asr = asr

    def run(self, audio_path: str | Path, target_text: str,
            utt_id: str = "session") -> SessionResult:
        hyp = self.asr.transcribe(str(audio_path))
        target, spoken = tokenize(target_text), tokenize(hyp["text"])
        pairs = align(target, spoken)

        word_errors = self.error_clf.predict(pairs, hyp["words"])
        n = max(len(word_errors), 1)
        rates: dict[str, float] = {}
        for e in word_errors:
            rates[e["label"]] = rates.get(e["label"], 0) + 1 / n
        accuracy = rates.get("correct", 0.0)

        pauses = pause_statistics(hyp["words"])
        duration_min = (hyp["words"][-1]["end"] / 60) if hyp["words"] else 1e-6
        wpm = len(spoken) / duration_min

        features = {"wpm": wpm, "accuracy": accuracy,
                    "error_rate": 1 - accuracy, **pauses,
                    **{f"{k}_rate": v for k, v in rates.items()}}
        score = self.risk_scorer.score(features)

        self.coach.seed_from_profile({k: v for k, v in rates.items() if k != "correct"})
        return SessionResult(
            utt_id=utt_id, wpm=wpm, accuracy=accuracy,
            word_errors=word_errors, error_rates=rates,
            risk_score=score, risk_band=self.risk_scorer.band(score),
            next_exercise=self.coach.select(),
            highlights=[{"index": e["position"], "label": e["label"]}
                        for e in word_errors if e["label"] != "correct"],
        )


def to_dict(result: SessionResult) -> dict:
    return asdict(result)

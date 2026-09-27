"""Module 4: confusable-pair detector.

Reuses the Module 1 CNN backbone but reframes the task: given a letter crop,
output the probability that it is one of a confusable pair AND which member.
Fuses two evidence streams at inference: handwriting (CNN) and speech (Module 2).
"""
from dataclasses import dataclass, field

CONFUSABLE_SETS = {"bd": ("b", "d"), "pq": ("p", "q"),
                   "mw": ("m", "w"), "nu": ("n", "u")}


@dataclass
class ConfusionProfile:
    """Running per-child tally of which pairs cause trouble."""
    counts: dict[str, int] = field(default_factory=dict)
    opportunities: dict[str, int] = field(default_factory=dict)

    def update(self, pair_key: str, confused: bool) -> None:
        self.opportunities[pair_key] = self.opportunities.get(pair_key, 0) + 1
        if confused:
            self.counts[pair_key] = self.counts.get(pair_key, 0) + 1

    def rates(self) -> dict[str, float]:
        return {
            k: self.counts.get(k, 0) / v
            for k, v in self.opportunities.items() if v >= 3
        }

    def weakest(self, top_k: int = 2) -> list[str]:
        return [k for k, _ in sorted(self.rates().items(),
                                     key=lambda kv: -kv[1])[:top_k]]


def fuse(handwriting_prob: float, speech_prob: float, w_hand: float = 0.5) -> float:
    """Late fusion of the two modalities into a single confusion score."""
    return w_hand * handwriting_prob + (1 - w_hand) * speech_prob

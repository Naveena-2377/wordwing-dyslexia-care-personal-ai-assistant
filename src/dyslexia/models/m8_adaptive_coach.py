"""Module 8: adaptive reading coach - which exercise next?

Thompson sampling over exercise types. Each arm keeps a Beta posterior of
'did this exercise produce measurable improvement for THIS child'. Cold start is
seeded from the child's error profile so the first sessions are already targeted.
"""
import random
from dataclasses import dataclass, field


@dataclass
class Arm:
    name: str
    alpha: float = 1.0
    beta: float = 1.0

    def sample(self) -> float:
        return random.betavariate(self.alpha, self.beta)

    def update(self, reward: float) -> None:
        self.alpha += reward
        self.beta += 1 - reward


ERROR_TO_ARM = {
    "reversal": "bd_pq_discrimination",
    "omission": "sight_word_drill",
    "mispronunciation": "phoneme_blending",
    "slow_decoding": "syllable_chunking",
    "substitution": "fluency_repeated_reading",
}


@dataclass
class AdaptiveCoach:
    arm_names: list[str]
    arms: dict[str, Arm] = field(default_factory=dict)
    history: list[str] = field(default_factory=list)
    max_repeat: int = 3

    def __post_init__(self):
        self.arms = {n: Arm(n) for n in self.arm_names}

    def seed_from_profile(self, error_rates: dict[str, float]) -> None:
        """Warm start: boost the prior of arms matching the child's top errors."""
        for err, rate in error_rates.items():
            arm = ERROR_TO_ARM.get(err)
            if arm in self.arms:
                self.arms[arm].alpha += 4.0 * rate

    def select(self) -> str:
        ranked = sorted(self.arms.values(), key=lambda a: -a.sample())
        for arm in ranked:
            tail = self.history[-self.max_repeat:]
            if len(tail) == self.max_repeat and all(h == arm.name for h in tail):
                continue          # forced variety - kids disengage on repetition
            self.history.append(arm.name)
            return arm.name
        return ranked[0].name

    def record(self, arm_name: str, improved: bool) -> None:
        self.arms[arm_name].update(1.0 if improved else 0.0)

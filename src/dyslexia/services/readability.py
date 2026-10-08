"""Quality guardrail: is the rewritten text complete and genuinely easier to read?"""
import re


def grade_level(text: str) -> float:
    import textstat

    return textstat.flesch_kincaid_grade(text)


def _sentence_count(text: str) -> int:
    return max(len([s for s in re.split(r"[.!?]+", text) if s.strip()]), 1)


def acceptable(original: str, simplified: str, max_avg_words: int = 15) -> bool:
    s = simplified.strip()
    if not s or s == original.strip():
        return False
    if s[-1] not in ".!?\"'":  # looks cut off mid-sentence
        return False
    words = len(s.split())
    if words < 3 or words / _sentence_count(s) > max_avg_words:
        return False
    return grade_level(s) < grade_level(original)


def passes(original: str, simplified: str, target_grade: float = 3.0, max_words: int = 12) -> bool:
    return acceptable(original, simplified)
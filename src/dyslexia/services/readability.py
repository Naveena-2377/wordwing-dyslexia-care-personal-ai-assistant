"""Guardrail: does the simplified output actually read easier?

Every simplifier output passes through here before it reaches a child.
If it fails, fall back to the LLM, then to the original sentence.
"""


def grade_level(text: str) -> float:
    import textstat

    return textstat.flesch_kincaid_grade(text)


def passes(original: str, simplified: str, target_grade: float = 3.0,
           max_words: int = 12) -> bool:
    if not simplified.strip():
        return False
    if len(simplified.split()) > max_words * 2:
        return False
    return (grade_level(simplified) <= target_grade
            and grade_level(simplified) < grade_level(original))

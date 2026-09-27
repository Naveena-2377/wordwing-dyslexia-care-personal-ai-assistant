import re
import string

_PUNCT = str.maketrans("", "", string.punctuation)


def normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace. Used before alignment."""
    text = text.lower().translate(_PUNCT)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    return normalize(text).split()


CONFUSABLE_PAIRS = [("b", "d"), ("p", "q"), ("m", "w"), ("n", "u"), ("b", "p"), ("d", "q")]


def is_reversal_error(target: str, spoken: str) -> bool:
    """True when the two words differ only by a known confusable letter swap."""
    if len(target) != len(spoken):
        return False
    diffs = [(a, b) for a, b in zip(target, spoken) if a != b]
    if not diffs or len(diffs) > 2:
        return False
    return all(tuple(sorted(d)) in [tuple(sorted(p)) for p in CONFUSABLE_PAIRS] for d in diffs)

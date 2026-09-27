"""Word-level alignment between the target text and what the child actually said.

This is the backbone of Module 2: before you can classify an error you must know
WHICH word went wrong and HOW. Needleman-Wunsch gives a full alignment (not just a
distance) so every target word gets an operation label.
"""
from dataclasses import dataclass


@dataclass
class AlignedPair:
    index: int
    target: str | None
    spoken: str | None
    op: str  # match | substitution | omission | insertion | reversal
    confidence: float | None = None  # Whisper's confidence for the spoken word, if known
    flag: str | None = None          # extra signal, e.g. "low_confidence"


def align(target: list[str], spoken: list[str],
          match=2, mismatch=-1, gap=-2) -> list[AlignedPair]:
    n, m = len(target), len(spoken)
    score = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        score[i][0] = score[i - 1][0] + gap
    for j in range(1, m + 1):
        score[0][j] = score[0][j - 1] + gap

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            diag = score[i - 1][j - 1] + (match if target[i - 1] == spoken[j - 1] else mismatch)
            score[i][j] = max(diag, score[i - 1][j] + gap, score[i][j - 1] + gap)

    pairs, i, j = [], n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            diag = score[i - 1][j - 1] + (match if target[i - 1] == spoken[j - 1] else mismatch)
            if score[i][j] == diag:
                op = "match" if target[i - 1] == spoken[j - 1] else "substitution"
                pairs.append(AlignedPair(i - 1, target[i - 1], spoken[j - 1], op))
                i, j = i - 1, j - 1
                continue
        if i > 0 and score[i][j] == score[i - 1][j] + gap:
            pairs.append(AlignedPair(i - 1, target[i - 1], None, "omission"))
            i -= 1
        else:
            pairs.append(AlignedPair(i, None, spoken[j - 1], "insertion"))
            j -= 1
    return list(reversed(pairs))


def detect_reversals(pairs: list[AlignedPair]) -> list[AlignedPair]:
    """Post-process aligned pairs: two adjacent substitutions that are actually
    a swapped word order (target[i]==spoken[i+1] and target[i+1]==spoken[i])
    get relabeled from 'substitution' to 'reversal'.

    Must run after align(). Does not change the list length or ordering.
    """
    result = list(pairs)
    k = 0
    while k < len(result) - 1:
        a, b = result[k], result[k + 1]
        if (a.op == "substitution" and b.op == "substitution"
                and a.target is not None and b.target is not None
                and a.spoken is not None and b.spoken is not None
                and a.target == b.spoken and b.target == a.spoken):
            a.op = "reversal"
            b.op = "reversal"
            k += 2
        else:
            k += 1
    return result


def attach_confidence(pairs: list[AlignedPair], whisper_words: list[dict],
                       low_conf_threshold: float = 0.6) -> list[AlignedPair]:
    """Attach Whisper's per-word confidence to each aligned pair's spoken word,
    and flag low-confidence matches as suspicious even when the aligner sees
    a clean 'match' or 'substitution'.

    whisper_words: the result["words"] list from STTService.transcribe(), each
    with 'word', 'start', 'end', 'prob'.

    Matching is done by order of appearance (spoken words are consumed in
    sequence), since Whisper's word list and the tokenized spoken list should
    correspond 1:1 in order.
    """
    conf_queue = list(whisper_words)
    for p in pairs:
        if p.spoken is None:
            continue
        if conf_queue:
            w = conf_queue.pop(0)
            p.confidence = w.get("prob")
            if p.confidence is not None and p.confidence < low_conf_threshold:
                p.flag = "low_confidence"
    return pairs
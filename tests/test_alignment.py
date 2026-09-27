from dyslexia.common.alignment import align
from dyslexia.common.text_utils import tokenize, is_reversal_error


def test_perfect_read_is_all_matches():
    t = tokenize("the cat sat on the mat")
    assert all(p.op == "match" for p in align(t, t))


def test_omission_detected():
    pairs = align(tokenize("the cat sat on the mat"), tokenize("cat sat on the mat"))
    assert any(p.op == "omission" and p.target == "the" for p in pairs)


def test_substitution_detected():
    pairs = align(tokenize("the dog ran"), tokenize("the bog ran"))
    assert any(p.op == "substitution" for p in pairs)


def test_bd_reversal():
    assert is_reversal_error("dog", "bog")
    assert not is_reversal_error("dog", "cat")

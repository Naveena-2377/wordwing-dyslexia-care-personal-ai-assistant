from dyslexia.data.synth_reading_errors import (inject_reversal, inject_transposition,
                                                corrupt_sentence)


def test_reversal_changes_one_letter():
    out = inject_reversal("bed")
    assert out is not None and len(out) == 3 and out != "bed"


def test_transposition_needs_length():
    assert inject_transposition("at") is None


def test_corrupt_sentence_labels_every_word():
    rates = {"reversal": 0.5, "omission": 0.2, "mispronunciation": 0.2,
             "slow_decoding": 0.1}
    recs = corrupt_sentence("the big elephant walked", rates)
    assert len(recs) == 4
    assert all("label" in r for r in recs)

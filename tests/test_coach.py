from dyslexia.models.m8_adaptive_coach import AdaptiveCoach


def test_seeding_biases_selection():
    coach = AdaptiveCoach(["bd_pq_discrimination", "sight_word_drill"])
    coach.seed_from_profile({"reversal": 0.9})
    picks = [coach.select() for _ in range(30)]
    assert picks.count("bd_pq_discrimination") > picks.count("sight_word_drill")


def test_no_more_than_three_repeats():
    coach = AdaptiveCoach(["a", "b"], max_repeat=3)
    picks = [coach.select() for _ in range(20)]
    for i in range(len(picks) - 3):
        assert len(set(picks[i:i + 4])) > 1

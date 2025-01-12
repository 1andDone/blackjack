def test_summary(stats):
    """Tests the summary method within the Stats class."""
    assert stats.summary(string=False) == {
        'TOTAL ROUNDS PLAYED': 2,
        'TOTAL HANDS PLAYED': 2,
        'PLAYER HANDS WON': 0,
        'PLAYER HANDS LOST': 2,
        'PLAYER HANDS PUSHED': 0,
        'PLAYER BLACKJACKS': 0,
        'DEALER BLACKJACKS': 1,
        'PLAYER DOUBLE DOWNS': 0,
        'PLAYER SURRENDERS': 0,
        'INSURANCE AMOUNT BET': 12.5,
        'INSURANCE NET WINNINGS': 25,
        'AMOUNT BET': 35,
        'NET WINNINGS': -35,
        'TOTAL AMOUNT BET': 47.5,
        'TOTAL NET WINNINGS': -10
    }

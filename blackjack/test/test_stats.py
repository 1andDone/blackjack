def test_summary_as_dictionary(stats):
    """
    Tests the summary method within the Stats class
    when it's a dictionary.
    
    """
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


def test_summary_as_string(stats):
    """
    Tests the summary method within the Stats class
    when it's a string.
    
    """
    assert stats.summary(string=True) == (
        'TOTAL ROUNDS PLAYED: 2\n'
        'TOTAL HANDS PLAYED: 2\n'
        'PLAYER HANDS WON: 0\n'
        'PLAYER HANDS LOST: 2\n'
        'PLAYER HANDS PUSHED: 0\n'
        'PLAYER BLACKJACKS: 0\n'
        'DEALER BLACKJACKS: 1\n'
        'PLAYER DOUBLE DOWNS: 0\n'
        'PLAYER SURRENDERS: 0\n'
        'INSURANCE AMOUNT BET: $12.50\n'
        'INSURANCE NET WINNINGS: $25.00\n'
        'AMOUNT BET: $35.00\n'
        'NET WINNINGS: -$35.00\n'
        'TOTAL AMOUNT BET: $47.50\n'
        'TOTAL NET WINNINGS: -$10.00'
    )

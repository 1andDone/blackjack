from blackjack.enums import StatsCategory
from blackjack.stats import Stats, StatsKey


def test_add_hand():
    """Tests the add_hand method within the Stats class."""
    stats = Stats()
    stats.add_hand(count=1, category=StatsCategory.PLAYER_HANDS_WON)
    assert stats.stats[StatsKey(count=1, category=StatsCategory.PLAYER_HANDS_WON)] == 1
    assert stats.stats[StatsKey(count=1, category=StatsCategory.TOTAL_HANDS_PLAYED)] == 1


def test_add_value(stats):
    """Tests the add_value method within the Stats class."""
    stats = Stats()
    stats.add_value(count=1, category=StatsCategory.NET_WINNINGS, value=5.5)
    assert stats.stats[StatsKey(count=1, category=StatsCategory.NET_WINNINGS)] == 5.5
    stats.add_value(count=1, category=StatsCategory.PLAYER_SURRENDERS)
    assert stats.stats[StatsKey(count=1, category=StatsCategory.PLAYER_SURRENDERS)] == 1


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

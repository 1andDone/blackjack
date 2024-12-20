from blackjack.enums import StatsCategory
from blackjack.stats import StatsKey


def test_add_hand(setup_stats):
    """Tests the add_hand method within the Stats class."""
    setup_stats.add_hand(count=1, category=StatsCategory.HANDS_WON)
    assert setup_stats.stats[StatsKey(count=1, category=StatsCategory.HANDS_WON)] == 1


def test_update_amount(setup_stats):
    """Tests the update_amount method within the Stats class."""
    setup_stats.update_amount(count=1, category=StatsCategory.AMOUNT_EARNED, increment=5.5)
    assert setup_stats.stats[StatsKey(count=1, category=StatsCategory.AMOUNT_EARNED)] == -4.5


def test_summary(setup_stats):
    """Tests the summary method within the Stats class."""
    assert setup_stats.summary == 'HANDS PLAYED: 2\nHANDS WON: 0\nHANDS LOST: 2\nHANDS PUSHED: 0\nAMOUNT EARNED: -$30.43\nAMOUNT WAGERED: $30.43\nINSURANCE AMOUNT EARNED: $0.00\nINSURANCE AMOUNT WAGERED: $0.00\nTOTAL AMOUNT EARNED: -$30.43\nTOTAL AMOUNT WAGERED: $30.43\nELEMENT OF RISK: -100.00%\n'

from blackjack.simulation_stats import StatsCategory, StatsKey


def test_add_hand(setup_simulation_stats):
    """Tests the add_hand method within the SimulationStats class."""
    setup_simulation_stats.add_hand(count=1, category=StatsCategory.HANDS_WON)
    assert setup_simulation_stats.stats[StatsKey(count=1, category=StatsCategory.HANDS_WON)] == 1


def test_add_amount(setup_simulation_stats):
    """Tests the add_amount method within the SimulationStats class."""
    setup_simulation_stats.add_amount(count=1, category=StatsCategory.AMOUNT_EARNED, increment=5.5)
    assert setup_simulation_stats.stats[StatsKey(count=1, category=StatsCategory.AMOUNT_EARNED)] == -4.5


def test_str(setup_simulation_stats):
    """Tests the __str__ method within the SimulationStats class."""
    assert str(setup_simulation_stats) == 'Hands lost: 2 \nHands played: 2 \nAmount wagered: $30.43 \nAmount earned: -$30.43 \nTotal amount earned: -$30.43 \nTotal amount wagered: $30.43 \nElement of Risk: -100.0% \n'
import pytest
from blackjack import CardCounter, CountingStrategy


def test_init_bet_ramp_maximum_exceeds_bankroll():
    """
    Tests the __init__ method within the CardCounter class
    when the player's bet ramp maximum bet exeeds the player's
    bankroll.
    """
    with pytest.raises(ValueError):
        CardCounter(
            name='Player 1',
            bankroll=1000,
            min_bet=10,
            counting_strategy=CountingStrategy.HI_LO,
            bet_ramp={
                1: 15,
                2: 20,
                3: 40,
                4: 50,
                5: 1001
            },
            insurance=None
        )


def test_init_bet_ramp_count_does_not_exist_float():
    """
    Tests the __init__ method within the CardCounter class
    when the player's bet ramp uses float values and
    one of the counts does not exist.
    """
    with pytest.raises(KeyError):
        CardCounter(
            name='Player 1',
            bankroll=1000,
            min_bet=10,
            counting_strategy=CountingStrategy.HALVES,
            bet_ramp={
                1.5: 15,
                2: 20,
                2.5: 40,
                3: 50,
                4: 80
            },
            insurance=None
        )


def test_init_bet_ramp_count_does_not_exist_integer():
    """
    Tests the __init__ method within the CardCounter class
    when the player's bet ramp uses integer values and one
    of the counts does not exist.
    """
    with pytest.raises(KeyError):
        CardCounter(
            name='Player 1',
            bankroll=1000,
            min_bet=10,
            counting_strategy=CountingStrategy.HI_LO,
            bet_ramp={
                1: 15,
                2: 20,
                3: 40,
                4: 50,
                6: 80
            },
            insurance=None
        )


@pytest.mark.parametrize(
    'test_count, expected',
    [
         (-5, 10),
         (1, 15),
         (6, 70)
     ]
)
def test_initial_wager(test_count, expected, setup_card_counter):
    """Tests the initial_wager method within the CardCounter class."""
    assert setup_card_counter.initial_wager(count=test_count) == expected
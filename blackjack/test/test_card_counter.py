import pytest
from blackjack.card_counter import CardCounter
from blackjack.enums import CardCountingSystem


def test_init_bet_ramp_maximum_exceeds_bankroll():
    """
    Tests the __init__ method within the CardCounter class
    when the player's bet ramp maximum bet exceeds the player's
    bankroll.

    """
    with pytest.raises(ValueError) as e:
        CardCounter(
            name='Player 2',
            bankroll=1000,
            min_bet=10,
            card_counting_system=CardCountingSystem.HI_LO,
            bet_ramp={
                1: 15,
                2: 20,
                3: 40,
                4: 50,
                5: 1001
            },
            insurance=None
        )
    assert str(e.value) == "Maximum bet in Player 2's bet ramp exceeds their bankroll."


def test_init_bet_ramp_count_does_not_exist_float():
    """
    Tests the __init__ method within the CardCounter class
    when the player's bet ramp uses float values and
    one of the counts does not exist and needs to be inferred.

    """
    card_counter = CardCounter(
        name='Player 2',
        bankroll=1000,
        min_bet=10,
        card_counting_system=CardCountingSystem.HALVES,
        bet_ramp={
            1.5: 15,
            2: 20,
            2.5: 40,
            3: 50,
            4: 80
        },
        insurance=None
    )
    assert card_counter._bet_ramp == {
        1.5: 15,
        2: 20,
        2.5: 40,
        3: 50,
        3.5: 50,
        4: 80
    }


def test_init_bet_ramp_count_does_not_exist_integer():
    """
    Tests the __init__ method within the CardCounter class
    when the player's bet ramp uses integer values and one
    of the counts does not exist and needs to be inferred.

    """
    card_counter = CardCounter(
        name='Player 2',
        bankroll=1000,
        min_bet=10,
        card_counting_system=CardCountingSystem.HI_LO,
        bet_ramp={
            1: 15,
            2: 20,
            3: 40,
            4: 50,
            6: 80
        },
        insurance=None
    )
    assert card_counter._bet_ramp == {
        1: 15,
        2: 20,
        3: 40,
        4: 50,
        5: 50,
        6: 80
    }


@pytest.mark.parametrize(
    'test_count, expected',
    [
        (-5, 10),
        (1, 15),
        (6, 70)
     ]
)
def test_placed_bet(card_counter_balanced, test_count, expected):
    """Tests the placed_bet method within the CardCounter class."""
    assert card_counter_balanced.placed_bet(count=test_count) == expected


def test_placed_bet_missing_count(card_counter_balanced):
    """
    Tests the placed_bet method within the CardCounter class
    when the kwargs is missing a count.

    """
    with pytest.raises(KeyError) as e:
        card_counter_balanced.placed_bet()
    assert str(e.value) == "'" + '"count" needs to be included in the kwargs.' + "'"

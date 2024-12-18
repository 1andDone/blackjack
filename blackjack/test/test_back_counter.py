import pytest
from blackjack.back_counter import BackCounter
from blackjack.enums import CountingStrategy


def test_init_partner_is_player(setup_player):
    """
    Tests the __init__ method within the BackCounter
    class when the partner is not a card counter and
    is a normal player.

    """
    with pytest.raises(TypeError) as e:
        BackCounter(
            name='Player 3',
            bankroll=1000,
            min_bet=10,
            counting_strategy=CountingStrategy.HI_LO,
            bet_ramp={
                1: 15,
                2: 20,
                3: 40,
                4: 50,
                5: 70
            },
            insurance=None,
            partner=setup_player,
            entry_point=3,
            exit_point=0
        )
    assert str(e.value) == "Player 3's partner must be a card counter."


def test_init_partner_is_back_counter(setup_back_counter):
    """
    Tests the __init__ method within the BackCounter
    class when the partner is not a card counter and
    is another back counter.

    """
    with pytest.raises(TypeError) as e:
        BackCounter(
            name='Player 3',
            bankroll=1000,
            min_bet=10,
            counting_strategy=CountingStrategy.HI_LO,
            bet_ramp={
                1: 15,
                2: 20,
                3: 40,
                4: 50,
                5: 70
            },
            insurance=None,
            partner=setup_back_counter,
            entry_point=3,
            exit_point=0
        )
    assert str(e.value) == "Player 3's partner must be a card counter."


def test_init_partner_different_counting_strategy(setup_card_counter):
    """
    Tests the __init__ method within the BackCounter
    class when the partner has a different counting strategy.

    """
    with pytest.raises(ValueError) as e:
        BackCounter(
            name='Player 3',
            bankroll=1000,
            min_bet=10,
            counting_strategy=CountingStrategy.KO,
            bet_ramp={
                1: 15,
                2: 20,
                3: 40,
                4: 50,
                5: 70
            },
            insurance=None,
            partner=setup_card_counter,
            entry_point=3,
            exit_point=0
        )
    assert str(e.value) == 'Player 3 must have the same card counting strategy as Player 2.'


@pytest.mark.parametrize(
    'test_entry_point, test_exit_point',
     [
         (1, 2),
         (2, 2)
     ]
)
def test_init_exit_point_gte_entry_point(test_entry_point, test_exit_point, setup_card_counter):
    """
    Tests the __init__ method within the BackCounter
    class when the exit point is greater than or equal
    to the entry point.

    """
    with pytest.raises(ValueError) as e:
        BackCounter(
            name='Player 3',
            bankroll=1000,
            min_bet=10,
            counting_strategy=CountingStrategy.HI_LO,
            bet_ramp={
                1: 15,
                2: 20,
                3: 40,
                4: 50,
                5: 70
            },
            insurance=None,
            partner=setup_card_counter,
            entry_point=test_entry_point,
            exit_point=test_exit_point
        )
    assert str(e.value) == 'Exit point must be less than the entry point.'


def test_init_exit_point_gt_insurance(setup_card_counter):
    """
    Tests the __init__ method within the BackCounter
    class when the exit point is greater than the
    point at which the player would purchase insurance.

    """
    with pytest.raises(ValueError) as e:
        BackCounter(
            name='Player 3',
            bankroll=1000,
            min_bet=10,
            counting_strategy=CountingStrategy.HI_LO,
            bet_ramp={
                1: 15,
                2: 20,
                3: 40,
                4: 50,
                5: 70
            },
            insurance=2,
            partner=setup_card_counter,
            entry_point=5,
            exit_point=3
        )
    assert str(e.value) == 'Exit point must be lower for player to take insurance bet.'


@pytest.mark.parametrize(
    'test_count, expected',
     [
         (4, True),
         (3, True),
         (2, False)
     ]
)
def test_can_enter(setup_back_counter, test_count, expected):
    """Tests the can_enter method within the BackCounter class."""
    assert setup_back_counter.can_enter(count=test_count) is expected


@pytest.mark.parametrize(
    'test_count, expected',
     [
         (1, False),
         (0, True),
         (-1, True)
     ]
)
def test_can_exit(setup_back_counter, test_count, expected):
    """Tests the can_exit method within the BackCounter class."""
    assert setup_back_counter.can_exit(count=test_count) is expected

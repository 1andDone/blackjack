import pytest
from blackjack import HouseRules


def test_init_invalid_shoe_size():
    """
    Tests the __init__ method within the HouseRules class
    when an invalid shoe size is provided.
    """
    with pytest.raises(ValueError):
        HouseRules(shoe_size=1, min_bet=10, max_bet=500)


def test_init_invalid_min_bet():
    """
    Tests the __init__ method within the HouseRules class
    when an invalid minimum bet is provided.
    """
    with pytest.raises(ValueError):
        HouseRules(shoe_size=6, min_bet=0, max_bet=500)


def test_init_min_bet_exceeds_max_bet():
    """
    Tests the __init__ method within the HouseRules class
    when the minimum bet exceeds the maximum bet.
    """
    with pytest.raises(ValueError):
        HouseRules(shoe_size=6, min_bet=500, max_bet=10)


def test_init_invalid_blackjack_payout():
    """
    Tests the __init__ method within the HouseRules class
    when an invalid blackjack payout is provided.
    """
    with pytest.raises(ValueError):
        HouseRules(shoe_size=6, min_bet=10, max_bet=500, blackjack_payout=0)


def test_init_invalid_max_hands():
    """
    Tests the __init__ method within the HouseRules class
    when an invalid max hands amount is provided.
    """
    with pytest.raises(ValueError):
        HouseRules(shoe_size=6, min_bet=10, max_bet=500, max_hands=1)


def test_init_resplit_aces_invalid_max_hands():
    """
    Tests the __init__ method within the HouseRules class
    when resplitting aces is allowed but an invalid max hands
    amount is provided.
    """
    with pytest.raises(ValueError):
        HouseRules(shoe_size=6, min_bet=10, max_bet=500, resplit_aces=True, max_hands=1)
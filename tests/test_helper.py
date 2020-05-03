import pytest

from helper import count_hand, max_count_hand, splittable
from house_rules import HouseRules


def test_count_hand():
    """
    Tests the count_hand function.

    """
    assert count_hand(hand=['K', '5', 'J']) == (25, 25)  # hand with no ace
    assert count_hand(hand=['A', '2', '4', '6']) == (23, 13)  # hand with single ace
    assert count_hand(hand=['A', 'A', 'Q', '3', '7']) == (32, 22)  # hand with multiple aces


def test_max_count_hand():
    """
    Tests the max_count_hand function.

    """
    assert max_count_hand(hand=['A', 'A', '5', '3']) == 20  # both hard and soft totals less than or equal to 21
    assert max_count_hand(hand=['A', 'A', 'K']) == 12  # soft total greater than 21


def test_splittable():
    """
    Tests the splittable function.

    """
    rules = HouseRules(
        min_bet=10,
        max_bet=500
    )
    assert splittable(rules=rules, hand=['A', 'A']) is True
    assert splittable(rules=rules, hand=['2', '2']) is True
    assert splittable(rules=rules, hand=['J', 'J']) is True
    assert splittable(rules=rules, hand=['2', '3']) is False


def test_splittable_split_unlike_tens():
    """
    Tests the splittable function on unlike 10 valued cards
    when split_unlike_tens is True.

    """
    rules = HouseRules(
        min_bet=10,
        max_bet=500,
        split_unlike_tens=True
    )
    assert splittable(rules=rules, hand=['J', '10']) is True
    assert splittable(rules=rules, hand=['Q', 'J']) is True
    assert splittable(rules=rules, hand=['K', 'Q']) is True


def test_splittable_no_split_unlike_tens():
    """
    Tests the splittable function on unlike 10 valued cards
    when split_unlike_tens is False.

    """
    rules = HouseRules(
        min_bet=10,
        max_bet=500,
        split_unlike_tens=False
    )
    assert splittable(rules=rules, hand=['J', '10']) is False
    assert splittable(rules=rules, hand=['Q', 'J']) is False
    assert splittable(rules=rules, hand=['K', 'Q']) is False


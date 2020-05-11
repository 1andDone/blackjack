import pytest
from house_rules import HouseRules
from helper import count_hand, max_count_hand, splittable


@pytest.mark.parametrize('hand, expected',
                         [
                             (['K', '5', 'J'], (25, 25)),  # no ace
                             (['A', '2', '4', '6'], (23, 13)),  # single ace
                             (['A', 'A', 'Q', '3', '7'], (32, 22))  # multiple aces
                         ])
def test_count_hand(hand, expected):
    """
    Tests the count_hand function.

    """
    assert count_hand(hand=hand) == expected


@pytest.mark.parametrize('hand, expected',
                         [
                             (['A', 'A', '5', '3'], 20),  # both hard and soft totals less than or equal to 21
                             (['A', 'A', 'K'], 12)  # soft total greater than 21
                         ])
def test_max_count_hand(hand, expected):
    """
    Tests the max_count_hand function.

    """
    assert max_count_hand(hand=hand) == expected


@pytest.mark.parametrize('split_unlike_tens, hand, expected',
                         [
                             (True, ['2', '2'], True),  # split
                             (True, ['2', '3'], False),  # not a split
                             (False, ['2', '2'], True),  # split
                             (False, ['2', '3'], False),  # not a split
                             (True, ['J', '10'], True),  # split unlike tens
                             (True, ['K', 'Q'], True),  # split unlike tens
                             (False, ['J', '10'], False),  # cannot split unlike tens
                             (False, ['K', 'Q'], False)  # cannot split unlike tens
                         ])
def test_splittable(split_unlike_tens, hand, expected):
    """
    Tests the splittable function.

    """
    rules = HouseRules(bet_limits=[10, 500], split_unlike_tens=split_unlike_tens)
    assert splittable(rules=rules, hand=hand) is expected

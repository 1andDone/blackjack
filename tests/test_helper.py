import pytest
from house_rules import HouseRules
from helper import count_hand, splittable


@pytest.mark.parametrize('hand, expected',
                         [
                             (['K', '5', 'J'], (25, False)),  # no ace, soft and hard totals are equivalent
                             (['A', '2', '4', '6'], (13, False)),  # single ace, soft hand is larger than 21
                             (['A', '2', '4'], (17, True)),  # single ace, soft hand is less than 21
                             (['A', 'A', '4', '3'], (19, True))  # multiple aces, one treated as 11, the other as 1
                         ])
def test_count_hand(hand, expected):
    """
    Tests the count_hand function.

    """
    assert count_hand(hand=hand) == expected


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

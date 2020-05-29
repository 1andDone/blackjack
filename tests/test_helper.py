import pytest
from house_rules import HouseRules
from helper import count_hand, splittable


@pytest.mark.parametrize('hand, expected',
                         [
                             ([13, 5, 11], (25, False)),  # no ace, soft and hard totals are equivalent
                             ([1, 2, 4, 6], (13, False)),  # single ace, soft hand is larger than 21
                             ([1, 2, 4], (17, True)),  # single ace, soft hand is less than 21
                             ([1, 1, 4, 3], (19, True))  # multiple aces, one treated as 11, the other as 1
                         ])
def test_count_hand(hand, expected):
    """
    Tests the count_hand function.

    """
    assert count_hand(hand=hand) == expected


@pytest.mark.parametrize('split_unlike_tens, hand, num_hands, expected',
                         [
                             (True, [2, 2], 1, True),  # split
                             (True, [2, 2], 4, False),  # reached max hands limit
                             (True, [2, 3], 1, False),  # not a split
                             (False, [2, 2], 1, True),  # split
                             (False, [2, 3], 1, False),  # not a split
                             (True, [11, 10], 1, True),  # split unlike tens
                             (True, [13, 12], 1, True),  # split unlike tens
                             (False, [11, 10], 1, False),  # cannot split unlike tens
                             (False, [13, 12], 1, False)  # cannot split unlike tens
                         ])
def test_splittable(split_unlike_tens, hand, num_hands, expected):
    """
    Tests the splittable function.

    """
    rules = HouseRules(
        shoe_size=4,
        bet_limits=[10, 500],
        split_unlike_tens=split_unlike_tens,
        max_hands=4
    )
    assert splittable(rules=rules, hand=hand, num_hands=num_hands) is expected

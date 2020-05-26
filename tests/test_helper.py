import pytest
from house_rules import HouseRules
from helper import count_hand, add_card_to_total, splittable


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


@pytest.mark.parametrize('total, soft_hand, card, expected',
                         [
                             (15, True, '4', (19, True)),  # soft 15 + 4 = soft 19
                             (15, True, 'J', (15, False)),  # soft 15 + 10 = hard 15
                             (15, False, '6', (21, False)),  # hard 15 + 6 = hard 21
                             (15, False, '7', (22, False)),  # hard 15 + 7 = hard 22
                             (4, False, 'A', (15, True)),  # hard 4 + 1/11 = soft 15
                             (10, False, 'A', (21, True)),  # hard 10 + 1/11 = soft 21
                             (20, False, 'A', (21, False))  # hard 20 + 1/11 = hard 21
                         ])
def test_add_card_to_total(total, soft_hand, card, expected):
    """
    Tests the add_card_to_total function.

    """
    assert add_card_to_total(total=total, soft_hand=soft_hand, card=card) == expected


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

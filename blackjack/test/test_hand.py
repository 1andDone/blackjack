import pytest
from blackjack.enums import HandStatus


def test_cards(hand_with_ace):
    """Tests the cards method within the Hand class."""
    assert hand_with_ace.cards == ['A', '6']


def test_status(hand_blackjack):
    """
    Tests the status getter and setter methods
    within the Hand class.

    """
    hand_blackjack.status = HandStatus.SETTLED
    assert hand_blackjack.status == HandStatus.SETTLED


def test_add_to_total_bet(hand_with_ace):
    """
    Tests the add_to_total_bet method within
    the Hand class.

    """
    hand_with_ace.add_to_total_bet(amount=10)
    assert hand_with_ace.total_bet == 10
    hand_with_ace.add_to_total_bet(amount=15)
    assert hand_with_ace.total_bet == 25


def test_add_to_side_bet(hand_with_ace):
    """
    Tests the add_to_side_bet method within
    the Hand class.

    """
    hand_with_ace.add_to_side_bet(amount=10)
    assert hand_with_ace.side_bet == 10
    hand_with_ace.add_to_side_bet(amount=15)
    assert hand_with_ace.side_bet == 25


def test_add_cards(hand_with_ace):
    """Tests the add_cards method within the Hand class."""
    assert hand_with_ace.cards == ['A', '6']
    hand_with_ace.add_card(card='K')
    assert hand_with_ace.cards == ['A', '6', 'K']


def test_number_of_cards(hand_with_ace):
    """Tests the number_of_cards method within the Hand class."""
    assert hand_with_ace.number_of_cards == 2
    hand_with_ace.add_card(card='8')
    assert hand_with_ace.number_of_cards == 3


def test_total(hand_with_ace):
    """Tests the total method within the Hand class."""
    assert hand_with_ace.total == 17
    hand_with_ace.add_card(card='9')
    assert hand_with_ace.total == 16


def test_is_soft_with_ace(hand_with_ace):
    """
    Tests the is_soft method within the Hand class when
    the hand contains an ace.

    """
    assert hand_with_ace.is_soft
    hand_with_ace.add_card(card='A')
    assert hand_with_ace.is_soft
    hand_with_ace.add_card(card='9')
    assert not hand_with_ace.is_soft


def test_is_soft_without_ace(hand_without_ace):
    """
    Tests the is_soft method within the Hand class when
    the hand does not contain an ace.

    """
    assert not hand_without_ace.is_soft


def test_is_busted(hand_without_ace):
    """Tests the is_busted method within the Hand class."""
    assert not hand_without_ace.is_busted
    hand_without_ace.add_card(card='3')
    assert not hand_without_ace.is_busted
    hand_without_ace.add_card(card='2')
    assert hand_without_ace.is_busted


def test_split(hand_pair):
    """Tests the split method within the Hand class."""
    assert hand_pair.cards == ['7', '7']
    new_hand = hand_pair.split()
    assert hand_pair.cards == ['7']
    assert hand_pair.is_split
    assert new_hand.cards == ['7']
    assert not new_hand.is_split


@pytest.mark.parametrize(
    'test_was_split, test_is_split, expected',
     [
        (False, True, False),
        (True, False, False),
        (True, True, False),
        (False, False, True)
     ]
)
def test_is_blackjack(hand_blackjack, test_was_split, test_is_split, expected):
    """
    Tests the is_blackjack method within the Hand class
    when the previous hand and current hand may or may not
    have been split.
    
    """
    hand_blackjack._was_split = test_was_split
    hand_blackjack._is_split = test_is_split
    assert hand_blackjack.total == 21
    assert hand_blackjack.is_blackjack is expected


def test_is_blackjack_too_many_cards(hand_without_ace):
    """
    Tests the is_blackjack method within the Hand class
    when the hand totals 21 but there are more than 2 cards
    in the hand.

    """
    assert not hand_without_ace.is_blackjack
    hand_without_ace.add_card(card='3')
    assert hand_without_ace.total == 21
    assert not hand_without_ace.is_blackjack

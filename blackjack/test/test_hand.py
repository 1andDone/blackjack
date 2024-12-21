import pytest
from blackjack.enums import HandStatus


def test_cards(setup_hand_with_ace):
    """Tests the cards method within the Hand class."""
    assert setup_hand_with_ace.cards == ['A', '6']


def test_status(setup_hand_blackjack):
    """
    Tests the status getter and setter methods
    within the Hand class.

    """
    setup_hand_blackjack.status = HandStatus.SETTLED
    assert setup_hand_blackjack.status == HandStatus.SETTLED


def test_add_to_total_bet(setup_hand_with_ace):
    """
    Tests the add_to_total_bet method within
    the Hand class.

    """
    setup_hand_with_ace.add_to_total_bet(amount=10)
    assert setup_hand_with_ace.total_bet == 10
    setup_hand_with_ace.add_to_total_bet(amount=15)
    assert setup_hand_with_ace.total_bet == 25


def test_add_to_side_bet(setup_hand_with_ace):
    """
    Tests the add_to_side_bet method within
    the Hand class.

    """
    setup_hand_with_ace.add_to_side_bet(amount=10)
    assert setup_hand_with_ace.side_bet == 10
    setup_hand_with_ace.add_to_side_bet(amount=15)
    assert setup_hand_with_ace.side_bet == 25


def test_add_cards(setup_hand_with_ace):
    """Tests the add_cards method within the Hand class."""
    assert setup_hand_with_ace.cards == ['A', '6']
    setup_hand_with_ace.add_card(card='K')
    assert setup_hand_with_ace.cards == ['A', '6', 'K']


def test_number_of_cards(setup_hand_with_ace):
    """Tests the number_of_cards method within the Hand class."""
    assert setup_hand_with_ace.number_of_cards == 2
    setup_hand_with_ace.add_card(card='8')
    assert setup_hand_with_ace.number_of_cards == 3


def test_total(setup_hand_with_ace):
    """Tests the total method within the Hand class."""
    assert setup_hand_with_ace.total == 17
    setup_hand_with_ace.add_card(card='9')
    assert setup_hand_with_ace.total == 16


def test_is_soft_with_ace(setup_hand_with_ace):
    """
    Tests the is_soft method within the Hand class when
    the hand contains an ace.

    """
    assert setup_hand_with_ace.is_soft
    setup_hand_with_ace.add_card(card='A')
    assert setup_hand_with_ace.is_soft
    setup_hand_with_ace.add_card(card='9')
    assert not setup_hand_with_ace.is_soft


def test_is_soft_without_ace(setup_hand_without_ace):
    """
    Tests the is_soft method within the Hand class when
    the hand does not contain an ace.

    """
    assert not setup_hand_without_ace.is_soft


def test_is_busted(setup_hand_without_ace):
    """Tests the is_busted method within the Hand class."""
    assert not setup_hand_without_ace.is_busted
    setup_hand_without_ace.add_card(card='3')
    assert not setup_hand_without_ace.is_busted
    setup_hand_without_ace.add_card(card='2')
    assert setup_hand_without_ace.is_busted


def test_split(setup_hand_split):
    """Tests the split method within the Hand class."""
    assert setup_hand_split.cards == ['7', '7']
    new_hand = setup_hand_split.split()
    assert setup_hand_split.cards == ['7']
    assert setup_hand_split.is_split
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
def test_is_blackjack(setup_hand_blackjack, test_was_split, test_is_split, expected):
    """
    Tests the is_blackjack method within the Hand class
    when the previous hand and current hand may or may not
    have been split.
    
    """
    setup_hand_blackjack._was_split = test_was_split
    setup_hand_blackjack._is_split = test_is_split
    assert setup_hand_blackjack.total == 21
    assert setup_hand_blackjack.is_blackjack is expected


def test_is_blackjack_too_many_cards(setup_hand_without_ace):
    """
    Tests the is_blackjack method within the Hand class
    when the hand totals 21 but there are more than 2 cards
    in the hand.

    """
    assert not setup_hand_without_ace.is_blackjack
    setup_hand_without_ace.add_card(card='3')
    assert setup_hand_without_ace.total == 21
    assert not setup_hand_without_ace.is_blackjack

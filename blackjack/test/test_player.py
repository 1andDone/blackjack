import pytest
from blackjack import Player


def test_init_insufficient_bankroll():
    """
    Tests the __init__ method within the Player class
    when the player has insufficient bankroll to place a bet.
    """
    with pytest.raises(ValueError):
        Player(name='Player 1', bankroll=1000, min_bet=1001)


def test_edit_bankroll(setup_player):
    """Tests the edit_bankroll method within the Player class."""
    setup_player.edit_bankroll(amount=10)
    assert setup_player.bankroll == 1010
    setup_player.edit_bankroll(amount=-20)
    assert setup_player.bankroll == 990
    
    
def test_has_sufficient_bankroll(setup_player):
    """Tests the has_sufficient_bankroll method within the Player class."""
    assert setup_player.has_sufficient_bankroll(amount=999)
    assert setup_player.has_sufficient_bankroll(amount=1000)
    assert not setup_player.has_sufficient_bankroll(amount=1001)


def test_hit(setup_player_without_split_hand):
    """Tests the hit method within the Player class."""
    hand = setup_player_without_split_hand.first_hand
    setup_player_without_split_hand.hit(hand=hand, card='5')
    assert hand.cards == ['8', '6', '5']
    

def test_split(setup_player_with_split_hand):
    """Tests the split method within the Player class."""
    hand = setup_player_with_split_hand.first_hand
    assert hand.cards == ['7', '7']
    setup_player_with_split_hand.split(hand=hand)
    split_hand = setup_player_with_split_hand.hands[1]
    assert hand.cards == ['7']
    assert split_hand.cards == ['7']


def test_decision_one_card(setup_player, setup_rules):
    """
    Tests the decision method within the Player class
    when there is one card in the hand.
    """
    setup_player.first_hand.add_card(card='8')
    assert setup_player.decision(hand=setup_player.first_hand, dealer_up_card='J', rules=setup_rules) == 'H'


def test_decision_number_of_hands_less_than_max_hands(setup_player, setup_rules):
    """
    Tests the decision method within the Player class
    when the number of hands is less than the max hands.
    """
    setup_player.first_hand.add_card(card='8')
    setup_player.first_hand.add_card(card='8')
    assert setup_player.decision(hand=setup_player.first_hand, dealer_up_card='J', rules=setup_rules) == 'P'


def test_decision_number_of_hands_equals_max_hands(setup_player, setup_rules):
    """
    Tests the decision method within the Player class
    when the number of hands equals the max hands.
    """
    setup_player.first_hand.add_card(card='8')
    setup_player.first_hand.add_card(card='8')
    setup_player.split(hand=setup_player.first_hand)
    setup_player.first_hand.add_card(card='J')
    assert setup_player.decision(hand=setup_player.first_hand, dealer_up_card='J', rules=setup_rules) == 'S'
    split_hand = setup_player.hands[1]
    split_hand.add_card(card='8')
    assert setup_player.decision(hand=split_hand, dealer_up_card='J', rules=setup_rules) == 'Rh'


def test_decision_soft(setup_player, setup_rules):
    """
    Tests the decision method within the Player class
    when the hand is soft.
    """
    setup_player.first_hand.add_card(card='7')
    setup_player.first_hand.add_card(card='A')
    assert setup_player.decision(hand=setup_player.first_hand, dealer_up_card='J', rules=setup_rules) == 'H'


def test_decision_hard(setup_player, setup_rules):
    """
    Tests the decision method within the Player class
    when the hand is hard.
    """
    setup_player.first_hand.add_card(card='8')
    setup_player.first_hand.add_card(card='K')
    assert setup_player.decision(hand=setup_player.first_hand, dealer_up_card='J', rules=setup_rules) == 'S'


def test_decision_busted(setup_player, setup_rules):
    """
    Tests the decision method within the Player class
    when the hand is busted.
    """
    setup_player.first_hand.add_card(card='K')
    setup_player.first_hand.add_card(card='J')
    setup_player.first_hand.add_card(card='2')
    with pytest.raises(KeyError):
        setup_player.decision(hand=setup_player.first_hand, dealer_up_card='J', rules=setup_rules)
        

def test_decision_pair(setup_player, setup_rules):
    """
    Tests the decision method within the Player class when
    the hand is a pair.
    """
    setup_player.first_hand.add_card(card='8')
    setup_player.first_hand.add_card(card='8')
    assert setup_player.decision(hand=setup_player.first_hand, dealer_up_card='J', rules=setup_rules) == 'P'


def test_decision_unlike_tens(setup_player, setup_rules):
    """
    Tests the decision method within the Player class when
    the hand is unlike tens.
    """
    setup_player.first_hand.add_card(card='J')
    setup_player.first_hand.add_card(card='Q')
    assert setup_player.decision(hand=setup_player.first_hand, dealer_up_card='A', rules=setup_rules) == 'S'


def test_reset_hands(setup_player_without_split_hand):
    """Tests the reset_hands method within the Player class."""
    hand = setup_player_without_split_hand.first_hand
    assert hand.cards == ['8', '6']
    setup_player_without_split_hand.reset_hands()
    reset_hand = setup_player_without_split_hand.first_hand
    assert reset_hand.cards == []
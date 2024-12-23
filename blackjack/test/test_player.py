import pytest
from blackjack.player import Player


def test_init_insufficient_bankroll():
    """
    Tests the __init__ method within the Player class
    when the player has insufficient bankroll to place a bet.

    """
    with pytest.raises(ValueError) as e:
        Player(name='Player 1', bankroll=1000, min_bet=1001)
    assert str(e.value) == "Insufficient bankroll to place Player 1's desired bet."


def test_adjust_bankroll(player):
    """Tests the adjust_bankroll method within the Player class."""
    player.adjust_bankroll(amount=10)
    assert player.bankroll == 1010
    player.adjust_bankroll(amount=-20)
    assert player.bankroll == 990


def test_has_sufficient_bankroll(player):
    """Tests the has_sufficient_bankroll method within the Player class."""
    assert player.has_sufficient_bankroll(amount=999)
    assert player.has_sufficient_bankroll(amount=1000)
    assert not player.has_sufficient_bankroll(amount=1001)


def test_decision_one_card(player, playing_strategy_s17):
    """
    Tests the decision method within the Player class
    when there is one card in the hand.

    """
    player.get_first_hand().add_card(card='8')
    assert player.decision(
        playing_strategy=playing_strategy_s17,
        hand=player.get_first_hand(),
        dealer_up_card='J',
        max_hands=4
    ) == 'H'


def test_decision_number_of_hands_less_than_max_hands(player, playing_strategy_s17):
    """
    Tests the decision method within the Player class
    when the number of hands is less than the max hands.

    """
    player.get_first_hand().add_card(card='8')
    player.get_first_hand().add_card(card='8')
    assert player.decision(
        playing_strategy=playing_strategy_s17,
        hand=player.get_first_hand(),
        dealer_up_card='J',
        max_hands=4
    ) == 'P'


def test_decision_number_of_hands_equals_max_hands(player, playing_strategy_s17):
    """
    Tests the decision method within the Player class
    when the number of hands equals the max hands.

    """
    player.get_first_hand().add_card(card='8')
    player.get_first_hand().add_card(card='8')
    split_card = player.get_first_hand().split()
    player.hands.append(split_card)
    player.get_first_hand().add_card(card='J')
    assert player.decision(
        playing_strategy=playing_strategy_s17,
        hand=player.get_first_hand(),
        dealer_up_card='J',
        max_hands=2
    ) == 'S'
    split_hand = player.hands[1]
    split_hand.add_card(card='8')
    assert player.decision(
        playing_strategy=playing_strategy_s17,
        hand=split_hand,
        dealer_up_card='J',
        max_hands=2
    ) == 'Rh'


def test_decision_soft(player, playing_strategy_s17):
    """
    Tests the decision method within the Player class
    when the hand is soft.

    """
    player.get_first_hand().add_card(card='7')
    player.get_first_hand().add_card(card='A')
    assert player.decision(
        playing_strategy=playing_strategy_s17,
        hand=player.get_first_hand(),
        dealer_up_card='J',
        max_hands=4
    ) == 'H'


def test_decision_hard(player, playing_strategy_s17):
    """
    Tests the decision method within the Player class
    when the hand is hard.

    """
    player.get_first_hand().add_card(card='8')
    player.get_first_hand().add_card(card='K')
    assert player.decision(
        playing_strategy=playing_strategy_s17,
        hand=player.get_first_hand(),
        dealer_up_card='J',
        max_hands=4
    ) == 'S'


def test_decision_busted(player, playing_strategy_s17):
    """
    Tests the decision method within the Player class
    when the hand is busted.

    """
    player.get_first_hand().add_card(card='K')
    player.get_first_hand().add_card(card='J')
    player.get_first_hand().add_card(card='2')
    with pytest.raises(KeyError):
        player.decision(
            playing_strategy=playing_strategy_s17,
            hand=player.get_first_hand(),
            dealer_up_card='J',
            max_hands=4
        )


def test_decision_pair(player, playing_strategy_s17):
    """
    Tests the decision method within the Player class when
    the hand is a pair.

    """
    player.get_first_hand().add_card(card='8')
    player.get_first_hand().add_card(card='8')
    assert player.decision(
        playing_strategy=playing_strategy_s17,
        hand=player.get_first_hand(),
        dealer_up_card='J',
        max_hands=4
    ) == 'P'


def test_decision_pair_insufficient_bankroll(player, playing_strategy_s17):
    """
    Tests the decision method within the Player class when
    the hand is a pair and the hand cannot be split
    due to insufficient bankroll.

    """
    player.get_first_hand().add_card(card='8')
    player.get_first_hand().add_card(card='8')
    player.get_first_hand().add_to_total_bet(amount=2000)
    assert player.decision(
        playing_strategy=playing_strategy_s17,
        hand=player.get_first_hand(),
        dealer_up_card='J',
        max_hands=4
    ) == 'Rh'


def test_reset_hands(player):
    """Tests the reset_hands method within the Player class."""
    player.get_first_hand().add_card(card='8')
    player.get_first_hand().add_card(card='8')
    split_card = player.get_first_hand().split()
    player.hands.append(split_card)
    player.get_first_hand().add_card(card='J')
    split_hand = player.hands[1]
    split_hand.add_card(card='9')
    assert player.number_of_hands == 2
    player.reset_hands()
    reset_hand = player.get_first_hand()
    assert not reset_hand.cards
    assert player.number_of_hands == 1

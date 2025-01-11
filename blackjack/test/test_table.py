import pytest
from blackjack.card_counter import CardCounter
from blackjack.enums import CardCountingSystem
from blackjack.player import Player
from blackjack.rules import Rules
from blackjack.table import Table


def test_add_player(table, player):
    """Tests the add_player method within the Table class."""
    table.add_player(player=player)
    assert table.players == [player]


def test_add_player_back_counter(table, back_counter):
    """
    Tests the add_player method within the Table class
    with a back counter.

    """
    table.add_player(player=back_counter)
    assert table.observers == [back_counter]


def test_add_player_not_player_instance(table, rules):
    """
    Tests the add_player method within the Table class
    with an object that is not an instance of the Player
    class.

    """
    with pytest.raises(TypeError) as e:
        table.add_player(player=rules)
    assert str(e.value) == 'Expected a Player, CardCounter, or BackCounter object.'


def test_add_player_bet_ramp_minimum_less_than_table_minimum(table):
    """
    Tests the add_player method within the Table class
    when the player's bet ramp minimum bet is less than the
    minimum allowed bet at the table.

    """
    player = CardCounter(
        name='Player 2',
        bankroll=1000,
        min_bet=10,
        card_counting_system=CardCountingSystem.HI_LO,
        bet_ramp={
            1: 5,
            2: 20,
            3: 40,
            4: 50,
            5: 70
        },
        insurance=None
    )
    with pytest.raises(ValueError) as e:
        table.add_player(player=player)
    assert str(e.value) == "Player 2's desired bet is not allowed according to the table rules."


def test_add_player_bet_ramp_maximum_exceeds_table_maximum(table):
    """
    Tests the add_player method within the Table class
    when the player's bet ramp maximum bet exceeds the maximum
    allowed bet at the table.

    """
    player =  CardCounter(
        name='Player 2',
        bankroll=10000,
        min_bet=10,
        card_counting_system=CardCountingSystem.HI_LO,
        bet_ramp={
            1: 15,
            2: 20,
            3: 40,
            4: 50,
            5: 1001
        },
        insurance=None
    )
    with pytest.raises(ValueError) as e:
        table.add_player(player=player)
    assert str(e.value) == "Player 2's desired bet is not allowed according to the table rules."


def test_add_player_no_insurance():
    """
    Tests the add_player method within the Table class
    when the player wants to buy insurance but it is not allowed.

    """
    rules = Rules(min_bet=10, max_bet=500, insurance=False)
    table = Table(rules=rules)
    player =  CardCounter(
        name='Player 2',
        bankroll=1000,
        min_bet=10,
        card_counting_system=CardCountingSystem.HI_LO,
        bet_ramp={
            1: 15,
            2: 20,
            3: 40,
            4: 50,
            5: 70
        },
        insurance=2
    )
    with pytest.raises(ValueError) as e:
        table.add_player(player=player)
    assert str(e.value) == "Player 2's insurance is not allowed according to the table rules."


def test_add_player_minimum_bet_less_than_table_minimum(table):
    """
    Tests the add_player method within the Table class
    when the player's minimum bet is less than the table minimum.

    """
    player = Player(name='Player 1', bankroll=1000, min_bet=5)
    with pytest.raises(ValueError) as e:
        table.add_player(player=player)
    assert str(e.value) == "Player 1's desired bet is not allowed according to the table rules."


def test_add_player_minimum_bet_greater_than_table_maximum(table):
    """
    Tests the add_player method within the Table class
    when player's minimum bet is greater than the table maximum.

    """
    player = Player(name='Player 1', bankroll=5000, min_bet=1500)
    with pytest.raises(ValueError) as e:
        table.add_player(player=player)
    assert str(e.value) == "Player 1's desired bet is not allowed according to the table rules."


def test_remove_player(table, player):
    """Tests the remove_player method within the Table class."""
    table.add_player(player=player)
    table.remove_player(player=player)
    assert not table.players


def test_remove_player_not_at_table(table, player):
    """
    Tests the remove_player method within the Table class
    when a player is not at the table.

    """
    with pytest.raises(ValueError) as e:
        table.remove_player(player=player)
    assert str(e.value) == 'Player 1 is not seated at the table or a back counter.'


def test_add_back_counter(table, back_counter):
    """Tests the add_back_counter method within the Table class."""
    table.add_player(player=back_counter)
    assert back_counter not in table.players
    assert back_counter in table.observers
    table.add_back_counter(back_counter=back_counter)
    assert back_counter in table.players
    assert back_counter not in table.observers
    assert back_counter.is_seated is True


def test_add_back_counter_non_back_counter(table, player):
    """
    Tests the add_back_counter method within the Table class
    when an attempt is made to add a non-back counter.

    """
    with pytest.raises(TypeError) as e:
        table.add_back_counter(back_counter=player)
    assert str(e.value) == 'Expected a BackCounter object.'


def test_remove_back_counter(table, back_counter):
    """Tests the remove_back_counter method within the Table class."""
    table.add_player(player=back_counter)
    table.add_back_counter(back_counter=back_counter)
    assert back_counter in table.players
    assert back_counter not in table.observers
    table.remove_back_counter(back_counter=back_counter)
    assert back_counter not in table.players
    assert back_counter in table.observers
    assert back_counter.is_seated is False


def test_remove_back_counter_non_back_counter(table, player):
    """
    Tests the remove_back_counter method within the Table class
    when an attempt is made to remove a non-back counter.

    """
    table.add_player(player=player)
    with pytest.raises(TypeError) as e:
        table.remove_back_counter(back_counter=player)
    assert str(e.value) == 'Expected a BackCounter object.'

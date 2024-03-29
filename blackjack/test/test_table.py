import pytest
from blackjack import Player, CardCounter, CountingStrategy
from blackjack.house_rules import HouseRules
from blackjack.table import Table


def test_add_player(setup_table, setup_player):
    """Tests the add_player method within the Table class."""
    setup_table.add_player(player=setup_player)
    assert setup_table.players == [setup_player]


def test_add_player_back_counter(setup_table, setup_back_counter):
    """
    Tests the add_player method within the Table class
    with a back counter.
    """
    setup_table.add_player(player=setup_back_counter)
    assert setup_table.waiting_players == [setup_back_counter]


def test_add_player_not_player_instance(setup_table, setup_rules):
    """
    Tests the add_player method within the Table class
    with an object that is not an instance of the Player
    class.
    """
    with pytest.raises(TypeError):
        setup_table.add_player(player=setup_rules)


def test_add_player_bet_ramp_minimum_less_than_table_minimum(setup_table):
    """
    Tests the add_player method within the Table class
    when the player's bet ramp minimum bet is less than the
    minimum allowed bet at the table.
    """
    player = CardCounter(
        name='Player 1',
        bankroll=1000,
        min_bet=10,
        counting_strategy=CountingStrategy.HI_LO,
        bet_ramp={
            1: 5,
            2: 20,
            3: 40,
            4: 50,
            5: 70
        },
        insurance=None
    )
    with pytest.raises(ValueError):
        setup_table.add_player(player=player)


def test_add_player_bet_ramp_maximum_exceeds_table_maximum(setup_table):
    """
    Tests the add_player method within the Table class
    when the player's bet ramp maximum bet exceeds the maximum
    allowed bet at the table.
    """
    player =  CardCounter(
        name='Player 1',
        bankroll=10000,
        min_bet=10,
        counting_strategy=CountingStrategy.HI_LO,
        bet_ramp={
            1: 15,
            2: 20,
            3: 40,
            4: 50,
            5: 1001
        },
        insurance=None
    )
    with pytest.raises(ValueError):
        setup_table.add_player(player=player)

        
def test_add_player_no_insurance():
    """
    Tests the add_player method within the Table class
    when the player wants to buy insurance but it is not allowed.
    """
    rules = HouseRules(min_bet=10, max_bet=500, insurance=False)
    table = Table(rules=rules)
    player =  CardCounter(
        name='Player 1',
        bankroll=1000,
        min_bet=10,
        counting_strategy=CountingStrategy.HI_LO,
        bet_ramp={
            1: 15,
            2: 20,
            3: 40,
            4: 50,
            5: 70
        },
        insurance=2
    )
    with pytest.raises(ValueError):
        table.add_player(player=player)


def test_add_player_minimum_bet_less_than_table_minimum(setup_table):
    """
    Tests the add_player method within the Table class
    when the player's minimum bet is less than the table minimum.
    """
    player = Player(name='Player 1', bankroll=1000, min_bet=5)
    with pytest.raises(ValueError):
        setup_table.add_player(player=player)


def test_add_player_minimum_bet_greater_than_table_maximum(setup_table):
    """
    Tests the add_player method within the Table class
    when player's minimum bet is greater than the table maximum.
    """
    player = Player(name='Player 1', bankroll=5000, min_bet=1500)
    with pytest.raises(ValueError):
        setup_table.add_player(player=player)


def test_remove_player(setup_table, setup_player):
    """Tests the remove_player method within the Table class."""
    setup_table.add_player(player=setup_player)
    setup_table.remove_player(player=setup_player)
    assert setup_table.players == []


def test_remove_player_not_at_table(setup_table, setup_player):
    """
    Tests the remove_player method within the Table class
    when a player is not at the table.
    """
    with pytest.raises(ValueError):
        setup_table.remove_player(player=setup_player)


def test_remove_back_counter(setup_table, setup_back_counter):
    """Tests the remove_back_counter method within the Table class."""
    setup_table.add_player(player=setup_back_counter)
    setup_table.add_back_counter(player=setup_back_counter)
    assert setup_back_counter in setup_table.players
    assert setup_back_counter not in setup_table.waiting_players
    setup_table.remove_back_counter(player=setup_back_counter)
    assert setup_back_counter not in setup_table.players
    assert setup_back_counter in setup_table.waiting_players


def test_remove_back_counter_insufficient_bankroll(setup_table, setup_back_counter):
    """
    Tests the remove_back_counter method within the Table class
    when the back counter has insufficient bankroll to be added
    to the waiting players
    """
    setup_table.add_player(player=setup_back_counter)
    setup_table.add_back_counter(player=setup_back_counter)
    assert setup_back_counter in setup_table.players
    assert setup_back_counter not in setup_table.waiting_players
    setup_back_counter.edit_bankroll(amount=-1000)
    setup_table.remove_back_counter(player=setup_back_counter)
    assert setup_back_counter not in setup_table.players
    assert setup_back_counter not in setup_table.waiting_players
    

def test_add_back_counter(setup_table, setup_back_counter):
    """Tests the back_counter_is_waiting method within the Table class."""
    setup_table.add_player(player=setup_back_counter)
    assert setup_back_counter not in setup_table.players
    assert setup_back_counter in setup_table.waiting_players
    setup_table.add_back_counter(player=setup_back_counter)
    assert setup_back_counter in setup_table.players
    assert setup_back_counter not in setup_table.waiting_players
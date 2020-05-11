import pytest
from table import Table
from player import Player
from house_rules import HouseRules


@pytest.fixture()
def setup_table():
    t = Table()
    r = HouseRules(bet_limits=[10, 500])
    p = Player(
            name='Player 1',
            rules=r,
            bankroll=100,
            min_bet=10
    )
    return t, p


class TestTable(object):

    @pytest.mark.parametrize('size_limit, expected',
                             [
                                 (0, ValueError),  # size limit < 1
                                 (8, ValueError),  # size limit > 7
                                 (7, 7)
                             ])
    def test_size_limit(self, size_limit, expected):
        """
        Tests the size_limit parameter of the __init__ method.

        """
        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                Table(size_limit=size_limit)

        else:
            t = Table(size_limit=size_limit)
            assert t.size_limit == expected

    @pytest.mark.parametrize('size_limit, player, expected',
                             [
                                 # players name exists at table
                                 (2,
                                  Player(
                                     name='Player 1',
                                     rules=HouseRules(bet_limits=[10, 500]),
                                     bankroll=100,
                                     min_bet=10),
                                  ValueError),

                                 # incorrect type
                                 (2,
                                  [Player(
                                     name='Player 1',
                                     rules=HouseRules(bet_limits=[10, 500]),
                                     bankroll=100,
                                     min_bet=10)],
                                  TypeError),

                                 # table at capacity
                                 (1,
                                  Player(
                                      name='Player 2',
                                      rules=HouseRules(bet_limits=[10, 500]),
                                      bankroll=100,
                                      min_bet=10),
                                  ValueError)
                             ])
    def test_add_player(self, setup_table, size_limit, player, expected):
        """
        Tests the add_player method.

        """
        t, p = setup_table
        t.size_limit = size_limit

        assert len(t.get_players()) == 0
        t.add_player(player=p)
        assert len(t.get_players()) == 1

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(tuple([TypeError, ValueError])):
                t.add_player(player=player)

    @pytest.mark.parametrize('player, expected',
                             [
                                  # remove player not at table
                                  (Player(
                                     name='Player 2',
                                     rules=HouseRules(bet_limits=[10, 500]),
                                     bankroll=100,
                                     min_bet=10),
                                   ValueError)
                             ])
    def test_remove_player(self, setup_table, player, expected):
        """
        Tests the remove_player method.

        """
        t, p = setup_table
        t.add_player(player=p)
        assert len(t.get_players()) == 1

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                t.remove_player(player=player)

        else:
            t.remove_player(player=p)
            assert len(t.get_players()) == 0




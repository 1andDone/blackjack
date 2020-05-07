import pytest
from table import Table
from player import Player
from house_rules import HouseRules


class TestTable(object):

    def test_init_no_size_limit(self):
        t = Table()
        assert t.size_limit == 7

    def test_init_incorrect_size_limit(self):
        with pytest.raises(ValueError):
            t = Table(size_limit=0)
        with pytest.raises(ValueError):
            t = Table(size_limit=8)

    def test_init_correct_size_limit(self):
        for size_limit in range(1, 8):
            t = Table(size_limit=size_limit)
            assert t.size_limit == size_limit
            assert t.players == []

    def test_add_player(self):
        t = Table()
        r = HouseRules(bet_limits=[10, 500])
        p = Player(
                name='Player 1',
                rules=r,
                bankroll=100,
                min_bet=10
        )
        assert len(t.get_players()) == 0
        t.add_player(player=p)
        assert len(t.get_players()) == 1

    def test_add_player_incorrect_instance(self):
        t = Table()
        r = HouseRules(bet_limits=[10, 500])
        p = [Player(
                name='Player 1',
                rules=r,
                bankroll=100,
                min_bet=10
        )]
        assert len(t.get_players()) == 0
        with pytest.raises(AttributeError):
            t.add_player(player=p)

    def test_add_player_name_exists(self):
        t = Table()
        r = HouseRules(bet_limits=[10, 500])
        p = Player(
                name='Player 1',
                rules=r,
                bankroll=100,
                min_bet=10
        )
        t.add_player(player=p)
        with pytest.raises(ValueError):
            t.add_player(player=p)

    def test_add_player_table_at_capacity(self):
        t = Table(size_limit=1)
        r = HouseRules(bet_limits=[10, 500])
        p = Player(
                name='Player 1',
                rules=r,
                bankroll=100,
                min_bet=10
        )
        t.add_player(player=p)
        with pytest.raises(ValueError):
            t.add_player(player=p)

    def test_remove_player(self):
        t = Table()
        r = HouseRules(bet_limits=[10, 500])
        p = Player(
                name='Player 1',
                rules=r,
                bankroll=100,
                min_bet=10
        )
        t.add_player(player=p)
        assert len(t.get_players()) == 1
        t.remove_player(player=p)
        assert len(t.get_players()) == 0

    def test_remove_player_player_not_at_table(self):
        t = Table()
        r = HouseRules(bet_limits=[10, 500])
        p = Player(
                name='Player 1',
                rules=r,
                bankroll=100,
                min_bet=10
        )
        assert len(t.get_players()) == 0
        with pytest.raises(ValueError):
            t.remove_player(player=p)


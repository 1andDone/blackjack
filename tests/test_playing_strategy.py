import pytest
from playing_strategy import PlayingStrategy
from house_rules import HouseRules
import basic_strategy


class TestPlayingStrategy(object):

    def test_init_no_argument(self):
        with pytest.raises(Exception):
            ps = PlayingStrategy()

    def test_init_incorrect_argument(self):
        rules = HouseRules(min_bet=10, max_bet=500)
        with pytest.raises(ValueError):
            ps = PlayingStrategy(rules='Incorrect argument', strategy='Basic')
        with pytest.raises(ValueError):
            ps = PlayingStrategy(rules=rules, strategy='Incorrect argument')

    def test_init_correct_argument(self):
        rules = HouseRules(min_bet=10, max_bet=500)
        ps = PlayingStrategy(rules=rules, strategy='Basic')
        assert isinstance(ps.rules, HouseRules)
        assert ps.strategy == 'Basic'

    def test_splits(self):
        rules = HouseRules(min_bet=10, max_bet=500, s17=True)
        ps = PlayingStrategy(rules=rules, strategy='Basic')
        assert ps.splits() == basic_strategy.s17_splits
        rules.s17 = False
        assert ps.splits() == basic_strategy.h17_splits

    def test_soft(self):
        rules = HouseRules(min_bet=10, max_bet=500, s17=True)
        ps = PlayingStrategy(rules=rules, strategy='Basic')
        assert ps.soft() == basic_strategy.s17_soft
        rules.s17 = False
        assert ps.soft() == basic_strategy.h17_soft

    def test_hard(self):
        rules = HouseRules(min_bet=10, max_bet=500, s17=True)
        ps = PlayingStrategy(rules=rules, strategy='Basic')
        assert ps.hard() == basic_strategy.s17_hard
        rules.s17 = False
        assert ps.hard() == basic_strategy.h17_hard

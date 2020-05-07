import pytest
from playing_strategy import PlayingStrategy
from house_rules import HouseRules
import basic_strategy


class TestPlayingStrategy(object):

    def test_init_no_rules(self):
        with pytest.raises(Exception):
            PlayingStrategy(strategy='Basic')

    def test_init_no_strategy(self):
        rules = HouseRules(bet_limits=[10, 500])
        with pytest.raises(Exception):
            PlayingStrategy(rules=rules)

    def test_init_incorrect_rules(self):
        with pytest.raises(ValueError):
            PlayingStrategy(rules='Incorrect argument', strategy='Basic')

    def test_init_incorrect_strategy(self):
        rules = HouseRules(bet_limits=[10, 500])
        with pytest.raises(ValueError):
            PlayingStrategy(rules=rules, strategy='Incorrect argument')

    def test_init_correct_rules_strategy(self):
        rules = HouseRules(bet_limits=[10, 500])
        ps = PlayingStrategy(rules=rules, strategy='Basic')
        assert ps.strategy == 'Basic'

    def test_splits(self):
        rules = HouseRules(bet_limits=[10, 500], s17=True)
        ps = PlayingStrategy(rules=rules, strategy='Basic')
        assert ps.splits() == basic_strategy.s17_splits
        rules.s17 = False
        assert ps.splits() == basic_strategy.h17_splits

    def test_soft(self):
        rules = HouseRules(bet_limits=[10, 500], s17=True)
        ps = PlayingStrategy(rules=rules, strategy='Basic')
        assert ps.soft() == basic_strategy.s17_soft
        rules.s17 = False
        assert ps.soft() == basic_strategy.h17_soft

    def test_hard(self):
        rules = HouseRules(bet_limits=[10, 500], s17=True)
        ps = PlayingStrategy(rules=rules, strategy='Basic')
        assert ps.hard() == basic_strategy.s17_hard
        rules.s17 = False
        assert ps.hard() == basic_strategy.h17_hard

import pytest
from playing_strategy import PlayingStrategy
from house_rules import HouseRules
import basic_strategy


class TestPlayingStrategy(object):

    @pytest.mark.parametrize('strategy, expected',
                             [
                                 ('Basic', 'Basic'),
                                 ('No Strategy', ValueError)
                             ])
    def test_strategy(self, strategy, expected):
        """
        Tests the strategy parameter of the __init__ method.

        """
        r = HouseRules(bet_limits=[10, 500])

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                PlayingStrategy(rules=r, strategy=strategy)

        else:
            ps = PlayingStrategy(rules=r, strategy=strategy)
            assert ps.strategy == strategy

    @pytest.mark.parametrize('s17, expected',
                             [
                                 (True, basic_strategy.s17_splits),
                                 (False, basic_strategy.h17_splits)
                             ])
    def test_splits(self, s17, expected):
        """
        Tests the splits method.

        """
        r = HouseRules(
            bet_limits=[10, 500],
            s17=s17
        )
        ps = PlayingStrategy(
            rules=r,
            strategy='Basic'
        )
        assert ps.splits() == expected

    @pytest.mark.parametrize('s17, expected',
                             [
                                 (True, basic_strategy.s17_soft),
                                 (False, basic_strategy.h17_soft)
                             ])
    def test_soft(self, s17, expected):
        """
        Tests the soft method.

        """
        r = HouseRules(
            bet_limits=[10, 500],
            s17=s17
        )
        ps = PlayingStrategy(
            rules=r,
            strategy='Basic'
        )
        assert ps.soft() == expected

    @pytest.mark.parametrize('s17, expected',
                             [
                                 (True, basic_strategy.s17_hard),
                                 (False, basic_strategy.h17_hard)
                             ])
    def test_hard(self, s17, expected):
        """
        Tests the hard method.

        """
        r = HouseRules(
            bet_limits=[10, 500],
            s17=s17
        )
        ps = PlayingStrategy(
            rules=r,
            strategy='Basic'
        )
        assert ps.hard() == expected

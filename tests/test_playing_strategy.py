import pytest
from playing_strategy import PlayingStrategy
from house_rules import HouseRules
import basic_strategy


@pytest.fixture()
def setup_playing_strategy():
    r = HouseRules(bet_limits=[10, 500])
    ps = PlayingStrategy(rules=r, strategy='Basic')
    return r, ps


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
            assert ps.get_strategy() == strategy

    @pytest.mark.parametrize('s17, expected',
                             [
                                 (True, basic_strategy.s17_splits),
                                 (False, basic_strategy.h17_splits)
                             ])
    def test_splits(self, setup_playing_strategy, s17, expected):
        """
        Tests the splits method.

        """
        r, ps = setup_playing_strategy
        r.s17 = s17
        assert ps.splits() == expected

    @pytest.mark.parametrize('s17, expected',
                             [
                                 (True, basic_strategy.s17_soft),
                                 (False, basic_strategy.h17_soft)
                             ])
    def test_soft(self, setup_playing_strategy, s17, expected):
        """
        Tests the soft method.

        """
        r, ps = setup_playing_strategy
        r.s17 = s17
        assert ps.soft() == expected

    @pytest.mark.parametrize('s17, expected',
                             [
                                 (True, basic_strategy.s17_hard),
                                 (False, basic_strategy.h17_hard)
                             ])
    def test_hard(self, setup_playing_strategy, s17, expected):
        """
        Tests the hard method.

        """
        r, ps = setup_playing_strategy
        r.s17 = s17
        assert ps.hard() == expected

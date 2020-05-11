import pytest
from betting_strategy import BettingStrategy


class TestBettingStrategy(object):

    @pytest.mark.parametrize('strategy, expected',
                             [
                                 ('Flat', 'Flat'),
                                 ('Spread', 'Spread'),
                                 ('Other', ValueError)
                             ])
    def test_strategy(self, strategy, expected):
        """
        Tests the strategy parameter of the __init__ method.

        """
        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                BettingStrategy(strategy=strategy)

        else:
            bs = BettingStrategy(strategy=strategy)
            assert bs.get_strategy() == expected

    @pytest.mark.parametrize('strategy, min_bet, bet_spread, bet_scale, count, expected',
                             [
                                 ('Flat', 10, 1, None, None, 10),
                                 ('Flat', 20.6, 1, None, None, 20.6),
                                 ('Spread', 10, 10, {1: 10, 2: 50}, -1, 10),
                                 ('Spread', 10, 10, {1: 10, 2: 50}, 1, 50),
                                 ('Spread', 10, 10, {1: 10, 2: 50}, 2.5, 100),
                             ])
    def test_initial_bet(self, strategy, min_bet, bet_spread, bet_scale, count, expected):
        """
        Tests the initial_bet method.

        """
        bs = BettingStrategy(strategy=strategy)
        initial_bet = bs.initial_bet(
                                min_bet=min_bet,
                                bet_spread=bet_spread,
                                bet_scale=bet_scale,
                                count=count
                        )

        assert initial_bet == expected



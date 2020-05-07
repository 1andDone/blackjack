import pytest
from betting_strategy import BettingStrategy


class TestBettingStrategy(object):

    def test_init_no_strategy(self):
        with pytest.raises(Exception):
            BettingStrategy()

    def test_init_incorrect_strategy(self):
        with pytest.raises(ValueError):
            BettingStrategy(strategy='Incorrect argument')

    def test_init_correct_strategy(self):
        assert BettingStrategy(strategy='Flat').strategy == 'Flat'
        assert BettingStrategy(strategy='Spread').strategy == 'Spread'

    def test_initial_bet_flat(self):
        bs = BettingStrategy(strategy='Flat')
        initial_bet = bs.initial_bet(
                                min_bet=10,
                                bet_spread=1,
                                bet_scale=None,
                                count=None,
                                count_strategy=None
        )
        assert initial_bet == 10

    def test_initial_bet_spread(self):
        bs = BettingStrategy(strategy='Spread')

        for count in [-1, 1, 3, 7]:
            initial_bet = bs.initial_bet(
                min_bet=10,
                bet_spread=10,
                bet_scale={1: 10, 5: 50},
                count=count,
                count_strategy='Hi-Lo'
            )

            if count < 1:
                assert initial_bet == 10
            elif count < 5:
                assert initial_bet == 50
            else:
                assert initial_bet == 100

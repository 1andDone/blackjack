import pytest

from house_rules import HouseRules


class TestHouseRules(object):

    def test_init_no_bet_limits(self):
        with pytest.raises(Exception):
            HouseRules()

    def test_init_incorrect_bet_limits(self):
        # bet limits negative
        with pytest.raises(ValueError):
            HouseRules(bet_limits=[-5, -1])

        # lower limit greater than upper limit
        with pytest.raises(ValueError):
            HouseRules(bet_limits=[500, 10])

        # bet limits equal
        with pytest.raises(ValueError):
            HouseRules(bet_limits=[100, 100])

        # bet limits not integers
        with pytest.raises(ValueError):
            HouseRules(bet_limits=[10.6, 500.7])

        # bet limits with 3+ integers
        with pytest.raises(ValueError):
            HouseRules(bet_limits=[10, 500, 20])

    def test_init_incorrect_blackjack_payout(self):
        # blackjack payout less than 1
        with pytest.raises(ValueError):
            HouseRules(bet_limits=[10, 500], blackjack_payout=0.5)

        # blackjack payout equal to 1
        with pytest.raises(ValueError):
            HouseRules(bet_limits=[10, 500], blackjack_payout=1)

    def test_init_incorrect_max_hands(self):
        # max hands < 2
        with pytest.raises(ValueError):
            HouseRules(bet_limits=[10, 500], max_hands=1)

        # max hands > 4
        with pytest.raises(ValueError):
            HouseRules(bet_limits=[10, 500], max_hands=5)

    def test_init_correct_bet_limits(self):
        assert HouseRules(bet_limits=[10, 500]).min_bet == 10
        assert HouseRules(bet_limits=[10, 500]).max_bet == 500

    def test_init_correct_blackjack_payout(self):
        assert HouseRules(bet_limits=[10, 500], blackjack_payout=1.2).blackjack_payout == 1.2

    def test_init_correct_max_hands(self):
        assert HouseRules(bet_limits=[10, 500], max_hands=3).max_hands == 3


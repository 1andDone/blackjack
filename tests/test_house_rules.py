import pytest
from house_rules import HouseRules


class TestHouseRules(object):

    @pytest.mark.parametrize('shoe_size, expected',
                             [
                                 (4, 4),
                                 (6, 6),
                                 (8, 8),
                                 (10, ValueError)
                             ])
    def test_shoe_size(self, shoe_size, expected):
        """
        Tests the shoe_size parameter of the __init__ method.

        """
        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                HouseRules(
                    shoe_size=shoe_size,
                    bet_limits=[10, 500]
                )

        else:
            r = HouseRules(
                    shoe_size=shoe_size,
                    bet_limits=[10, 500]
                )
            assert r.shoe_size == expected

    @pytest.mark.parametrize('bet_limits, expected',
                             [
                                 ([-5, -1], ValueError),  # negative bet limits
                                 ([500, 100], ValueError),  # lower limit greater than upper limit
                                 ([100, 100], ValueError),  # equal bet limits
                                 ([10.6, 500.7], TypeError),  # non-integer bet limits
                                 ([10, 500, 20], ValueError),  # 3+ integer bet limits
                                 ([10, 500], [10, 500])
                             ])
    def test_bet_limits(self, bet_limits, expected):
        """
        Tests the bet_limits parameter of the __init__ method.

        """
        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(tuple([TypeError, ValueError])):
                HouseRules(
                    shoe_size=4,
                    bet_limits=bet_limits
                )

        else:
            rules = HouseRules(
                        shoe_size=4,
                        bet_limits=bet_limits
            )
            assert rules.min_bet == expected[0]
            assert rules.max_bet == expected[1]

    @pytest.mark.parametrize('blackjack_payout, expected',
                             [
                                 (0.5, ValueError),  # blackjack payout less than 1
                                 (1, ValueError),  # blackjack payout equal to 1
                                 (1.2, 1.2)
                             ])
    def test_blackjack_payout(self, blackjack_payout, expected):
        """
        Tests the blackjack_payout parameter of the __init__ method.

        """
        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                HouseRules(
                    shoe_size=4,
                    bet_limits=[10, 500],
                    blackjack_payout=blackjack_payout
                )

        else:
            rules = HouseRules(
                        shoe_size=4,
                        bet_limits=[10, 500],
                        blackjack_payout=blackjack_payout
            )
            assert rules.blackjack_payout == expected

    @pytest.mark.parametrize('resplit_aces, max_hands, expected',
                             [
                                 (False, 1, ValueError),  # max hands < 2
                                 (False, 5, ValueError),  # max hands > 4
                                 (True, 2, ValueError),  # re-split aces is allowed, max hands < 3
                                 (True, 3, 3),
                                 (False, 2, 2)
                             ])
    def test_max_hands(self, resplit_aces, max_hands, expected):
        """
        Tests the max_hands parameter of the __init__ method.

        """
        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                HouseRules(
                    shoe_size=4,
                    bet_limits=[10, 500],
                    resplit_aces=resplit_aces,
                    max_hands=max_hands
                )

        else:
            rules = HouseRules(
                shoe_size=4,
                bet_limits=[10, 500],
                resplit_aces=resplit_aces,
                max_hands=max_hands
            )
            assert rules.max_hands == expected




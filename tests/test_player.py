import pytest
from player import Player
from house_rules import HouseRules


@pytest.fixture
def setup_player():
    r = HouseRules(
        shoe_size=4,
        bet_limits=[10, 500]
    )
    p = Player(
            name='Player 1',
            rules=r,
            bankroll=100,
            min_bet=10
    )
    return p


class TestPlayer(object):

    @pytest.mark.parametrize('name, expected',
                             [
                                 ('Player 1', 'Player 1'),  # string name
                                 (1, TypeError)  # non-string name
                             ])
    def test_name(self, name, expected):
        """
        Tests the name parameter of the __init__ method.

        """
        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(TypeError):
                Player(
                    name=name,
                    rules=HouseRules(
                        shoe_size=4,
                        bet_limits=[10, 500]
                    ),
                    bankroll=100,
                    min_bet=10
                )

        else:
            p = Player(
                    name=name,
                    rules=HouseRules(
                        shoe_size=4,
                        bet_limits=[10, 500]
                    ),
                    bankroll=100,
                    min_bet=10
                )
            assert p.name == expected

    @pytest.mark.parametrize('bankroll, expected',
                             [
                                 (5, ValueError),  # bankroll is less than rules and/or players min bet
                                 (1000, 1000)
                             ])
    def test_bankroll(self, bankroll, expected):
        """
        Tests the bankroll parameter of the __init__ method.

        """
        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                Player(
                    name='Player 1',
                    rules=HouseRules(
                        shoe_size=4,
                        bet_limits=[10, 500]
                    ),
                    bankroll=bankroll,
                    min_bet=10
                )

        else:
            p = Player(
                    name='Player 1',
                    rules=HouseRules(
                        shoe_size=4,
                        bet_limits=[10, 500]
                    ),
                    bankroll=bankroll,
                    min_bet=10
                )
            assert p.bankroll == expected

    @pytest.mark.parametrize('min_bet, expected',
                             [
                                 (5, ValueError),  # min bet is less than rules allow
                                 (505, ValueError),  # min bet is greater than rules allow
                                 (10, 10)
                             ])
    def test_min_bet(self, min_bet, expected):
        """
        Tests the min_bet parameter of the __init__ method.

        """
        r = HouseRules(
            shoe_size=4,
            bet_limits=[10, 500]
        )

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=min_bet
                )

        else:
            p = Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=min_bet
                )
            assert p.min_bet == expected

    @pytest.mark.parametrize('bet_spread, expected',
                             [
                                 (0.5, ValueError),  # bet spread less than 1
                                 (10, 10),
                                 (50, ValueError)  # bet spread greater than rules max bet/player min bet
                             ])
    def test_bet_spread(self, bet_spread, expected):
        """
        Tests the bet_spread parameter of the __init__ method.

        """
        r = HouseRules(
            shoe_size=4,
            bet_limits=[10, 500]
        )

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=20,
                    bet_count_amount=[(1, 20), (2, 50)],
                    bet_spread=bet_spread,
                    bet_strategy='Spread',
                    count_strategy='Hi-Lo'
                )

        else:
            p = Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=20,
                    bet_count_amount=[(1, 20), (2, 50)],
                    bet_spread=bet_spread,
                    bet_strategy='Spread',
                    count_strategy='Hi-Lo'
            )
            assert p.bet_spread == expected

    @pytest.mark.parametrize('bet_count_amount, expected',
                             [
                                 ([(1, 10), (2, 50)], {1: 10, 2: 50}),
                                 ([(1, 10), (2, 50.56339)], {1: 10, 2: 50.56}),  # rounded
                                 ([(1, 15), (2, 50)], ValueError),  # first amount is greater than minimum bet
                                 ([(1, 10), (2, 105)], ValueError),  # last amount exceeds minimum bet * bet spread
                                 ([(2, 50), (1, 10)], ValueError),  # counts out of order
                                 ([(1, 50), (2, 10)], ValueError)  # amounts out of order
                             ])
    def test_bet_count_amount(self, bet_count_amount, expected):
        """
        Tests the bet_count_amount of the __init__ method.

        """
        r = HouseRules(
            shoe_size=4,
            bet_limits=[10, 500]
        )

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=10,
                    bet_count_amount=bet_count_amount,
                    bet_spread=10,
                    bet_strategy='Spread',
                    count_strategy='Hi-Lo'
                )

        else:
            p = Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=10,
                    bet_count_amount=bet_count_amount,
                    bet_spread=10,
                    bet_strategy='Spread',
                    count_strategy='Hi-Lo'
            )
            assert p.bet_ramp == expected

    @pytest.mark.parametrize('count_strategy, insurance, back_counting, back_counting_entry_exit, expected',
                             [
                                 ('Hi-Lo', None, True, [2, 1], [2, 1]),
                                 ('Hi-Lo', None, True, [2.2, -1.7], [2.2, -1.7]),
                                 ('Hi-Lo', None, True, [1, 2], ValueError),  # exit point is greater than entry point
                                 ('Hi-Lo', None, True, [3, 2, 1], ValueError),  # needs to be a list of length 2
                                 ('Hi-Lo', None, True, ['6', '5'], ValueError),  # needs to be int or float
                                 ('Hi-Lo', None, False, [2, 1], ValueError),  # no back counting
                                 ('Hi-Lo', None, True, None, ValueError),  # no back counting
                                 (None, None, True, [2, 1], ValueError),  # back counting requires a count strategy
                                 ('Hi-Lo', 1, True, [3, 2], ValueError),  # exit point needs to be <= to insurance
                                 ('Hi-Lo', 1, True, [3, 0], [3, 0])
                             ])
    def test_back_counting_entry_exit(
            self, count_strategy, insurance, back_counting, back_counting_entry_exit, expected
    ):
        """
        Tests the back_counting of the __init__ method.

        """
        r = HouseRules(
            shoe_size=4,
            bet_limits=[10, 500]
        )

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=10,
                    bet_count_amount=[(1, 10), (2, 50)],
                    bet_spread=10,
                    bet_strategy='Spread',
                    count_strategy=count_strategy,
                    insurance=insurance,
                    back_counting=back_counting,
                    back_counting_entry_exit=back_counting_entry_exit
                )

        else:
            p = Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=10,
                    bet_count_amount=[(1, 10), (2, 50)],
                    bet_spread=10,
                    bet_strategy='Spread',
                    count_strategy=count_strategy,
                    insurance=insurance,
                    back_counting=back_counting,
                    back_counting_entry_exit=back_counting_entry_exit
            )
            assert p.back_counting_entry == expected[0]
            assert p.back_counting_exit == expected[1]

    def test_set_hand(self, setup_player):
        """
        Tests the set_hand method.

        """
        p = setup_player
        assert p.hands_dict is None
        p.set_hand()
        assert p.hands_dict == {
            1:
                {
                    'busted': False,
                    'double down': False,
                    'hand': [],
                    'insurance': False,
                    'natural blackjack': False,
                    'settled natural blackjack': False,
                    'split': False,
                    'stand': False,
                    'surrender': False}
        }

    def test_hit(self, setup_player):
        """
        Tests the hit method.

        """
        p = setup_player
        p.set_hand()
        assert p.get_hand(key=1) == []
        p.hit(key=1, new_card=13)
        p.hit(key=1, new_card=7)
        assert p.get_hand(key=1) == [13, 7]

    def test_set_split(self, setup_player):
        """
        Tests the set_split method.

        """
        p = setup_player
        p.set_hand()
        p.hit(key=1, new_card=1)
        p.hit(key=1, new_card=1)
        assert p.get_hand(key=1) == [1, 1]
        p.set_split(key=1, new_key=2)
        for key in [1, 2]:
            assert p.get_hand(key=key) == [1]

    def test_set_double_down(self, setup_player):
        """
        Tests the set_double_down method.

        """
        p = setup_player
        p.set_hand()
        p.hit(key=1, new_card=6)
        p.hit(key=1, new_card=4)
        assert p.get_double_down(key=1) is False
        p.set_double_down(key=1, new_card=1)
        assert p.get_double_down(key=1) is True

    @pytest.mark.parametrize('total, hand, pair, soft_hand, expected',
                             [
                                 (8, [8], False, False, 'H'),  # hand of length 1
                                 (16, [8, 8], True, False, 'P'),  # number of hands is less than max hands
                                 (16, [8, 8], False, False, 'Rh'),  # number of hands is not less than max hands
                                 (18, [1, 7], False, True, 'H'),  # soft total
                                 (19, [8, 11], False, False, 'S'),  # hard total
                                 (26, [11, 6, 13], False, False, KeyError)  # busted hands are not in table
                             ])
    def test_decision(self, setup_player, total, hand, pair, soft_hand, expected):
        """
        Tests the decision method.

        """
        p = setup_player

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(KeyError):
                decision = p.decision(
                                total=total,
                                hand=hand,
                                pair=pair,
                                soft_hand=soft_hand,
                                dealer_up_card=11
                )
        else:
            decision = p.decision(
                total=total,
                hand=hand,
                pair=pair,
                soft_hand=soft_hand,
                dealer_up_card=11
            )
            assert decision == expected

